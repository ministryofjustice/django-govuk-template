import os
import re
import threading
import warnings

from django.apps import apps
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.handlers.wsgi import WSGIHandler
from django.core.management import CommandError, call_command
from django.core.management.commands.runserver import Command as RunserverCommand
try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:
    FileSystemEventHandler, Observer = object, None

base_options = ('verbosity', 'settings', 'pythonpath', 'traceback', 'no_color')
reload_script_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'devserver.js')


class Command(RunserverCommand, FileSystemEventHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.watched_apps = []
        self.build_delay = 1
        self.build_timer = None
        self.build_options = {}
        self.serve_static = False

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--watch-app', nargs='*', dest='watched_apps',
            help='Watch source assets for changes and rebuild them.',
        )
        parser.add_argument(
            '--build-delay', default=self.build_delay, type=int,
            help='Time to delay rebuild (seconds).',
        )

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('devserver is only available in DEBUG mode')
        if not options['use_threading']:
            raise CommandError('Threading is required')
        self.watched_apps = options.pop('watched_apps')
        if self.watched_apps:
            try:
                self.watched_apps = [apps.get_app_config(app_label) for app_label in self.watched_apps]
            except (LookupError, ImportError) as e:
                raise CommandError('%s. Are you sure your INSTALLED_APPS setting is correct?' % e)
        else:
            self.watched_apps = apps.get_app_configs()
        self.serve_static = 'django.contrib.staticfiles' in (a.name for a in apps.get_app_configs())
        self.build_delay = options['build_delay']
        self.build_options = {option: options[option] for option in base_options}
        if not Observer:
            warnings.warn('watchdog is not available, try installing using [watch] extra')
        elif not options['use_reloader'] or os.environ.get('RUN_MAIN'):
            # try to only run one observer and websocket
            self.setup_observer()
            self.setup_reload_socket()
        return super().handle(*args, **options)

    def setup_observer(self):
        observer = Observer()
        watched_app_paths = (os.path.join(app_config.path, 'static-src', 'stylesheets')
                             for app_config in self.watched_apps)
        watched_app_paths = filter(os.path.isdir, watched_app_paths)
        for watched_app_path in watched_app_paths:
            observer.schedule(self, watched_app_path, recursive=True)
        observer.daemon = True
        observer.start()

    def setup_reload_socket(self):
        reload_socket = ReloadSocket()
        reload_socket.daemon = True
        reload_socket.start()

    def on_created(self, event):
        self.schedule_build(event.src_path)

    def on_modified(self, event):
        self.schedule_build(event.src_path)

    def schedule_build(self, path):
        if not path.lower().endswith('.scss'):
            return
        if self.build_options['verbosity']:
            self.stdout.write('Scheduling `buildscss`')
        if self.build_timer:
            self.build_timer.cancel()
        # TODO: only build apps with changed paths?
        self.build_timer = threading.Timer(self.build_delay, call_command,
                                           args=('buildscss',),
                                           kwargs=self.build_options)
        self.build_timer.start()

    def get_handler(self, *args, **options):
        handler = super().get_handler(*args, **options)
        handler = ReloadHandler(handler)
        if self.serve_static:
            handler = StaticFilesHandler(handler)
        return handler


class ReloadHandler(WSGIHandler):
    def __init__(self, application):
        self.application = application
        super().__init__()

    def should_handle(self, response):
        content_type = response['content-type']
        return Observer and response.status_code == 200 and not response.streaming and \
            (content_type == 'text/html' or content_type.startswith('text/html;'))

    def get_response(self, request):
        response = super().get_response(request)
        if self.should_handle(response):
            encoding = response.encoding if hasattr(response, 'encoding') else 'utf-8'
            content = response.content.decode(encoding)
            script_tag = self.get_script_tag()
            content = re.sub(r'</head>', script_tag + '</head>', content,
                             count=1, flags=re.IGNORECASE)
            response.content = content.encode(encoding)
            if response.has_header('content-length'):
                response['content-length'] = len(response.content)
        return response

    def get_script_tag(self):
        with open(reload_script_path, 'rt') as f:
            return '<script async>%s</script>' % f.read()
