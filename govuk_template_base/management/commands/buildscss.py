import functools
from pathlib import Path
from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand, CommandError

try:
    import sass
except ImportError:
    sass = None

from govuk_template_base.apps import BaseAppConfig

OUTPUT_STYLES = list(sass.OUTPUT_STYLES.keys()) if sass else ['nested', 'expanded', 'compact', 'compressed']


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_labels', nargs='*',
                            help='Limit SCSS building to these apps.')
        parser.add_argument('--collect', action='store_true',
                            help='Save output CSS in collected static files location.')
        parser.add_argument('--output-style', choices=OUTPUT_STYLES, default='nested',
                            help='CSS output style.')

    def handle(self, *app_labels, **options):
        if app_labels:
            try:
                app_configs = [apps.get_app_config(app_label) for app_label in app_labels]
            except (LookupError, ImportError) as e:
                raise CommandError('%s. Are you sure your INSTALLED_APPS setting is correct?' % e)
        else:
            app_configs = apps.get_app_configs()
        verbosity = options['verbosity']
        output_style = options['output_style']
        collected_dest = options['collect'] and Path(settings.STATIC_ROOT)
        paths = [
            (app_config.source_path, collected_dest or app_config.static_path)
            for app_config in app_configs
            if isinstance(app_config, BaseAppConfig)
        ]
        include_paths = [source_path for source_path, _ in paths]  # TODO: make includes configurable
        compiler = Compiler(output_style=output_style, include_paths=include_paths)
        for source_path, dest_path in paths:
            if not source_path.is_dir():
                continue
            if verbosity > 1:
                self.stdout.write('Compiling SCSS files in %s' % source_path)
            compiler.compile(source_path, dest_path)


class Compiler:
    resolution_patterns = [
        '%s', '_%s', '_%s.scss', '%s.scss', '%s_index.scss',
    ]

    def __init__(self, output_style='nested', include_paths=(),
                 govuk_template_app=None, govuk_template_source_path=None):
        if sass is None:
            raise CommandError('libsass is not available, try installing using [scss] extra')

        self.output_style = output_style
        self.include_paths = [str(path) for path in include_paths]

        static_url = settings.STATIC_URL
        if static_url and not static_url.endswith('/'):
            static_url += '/'
        self.static_url = static_url

        if apps.is_installed('django.contrib.staticfiles'):
            from django.contrib.staticfiles.storage import staticfiles_storage

            self.get_static_url = staticfiles_storage.url
        else:
            self.get_static_url = functools.partial(urljoin, static_url)

        media_url = settings.MEDIA_URL
        if media_url and not media_url.endswith('/'):
            media_url += '/'
        self.get_media_url = functools.partial(urljoin, media_url)

        self.govuk_template_base_source_path = apps.get_app_config('govuk_template_base').source_path

        if govuk_template_app and govuk_template_source_path:
            self.govuk_template_app = govuk_template_app
            self.govuk_template_source_path = Path(govuk_template_source_path)
        else:
            govuk_template_config = next(filter(lambda app: getattr(app, 'govuk_template', False),
                                                apps.get_app_configs()), None)
            if not govuk_template_config:
                raise CommandError('Cannot find custom govuk_template app config')
            self.govuk_template_app = govuk_template_config.name
            self.govuk_template_source_path = govuk_template_config.source_path

    def govuk_template_functions(self):
        return {
            sass.SassFunction('django-static', ('$path',), lambda path: 'url("%s")' % self.get_static_url(path)),
            sass.SassFunction('django-media', ('$path',), lambda path: 'url("%s")' % self.get_media_url(path)),
        }

    def govuk_template_importers(self, path: str):
        if path == 'govuk_template_base/settings':
            return [('',
                     '/* Asset paths required by GOV.UK design system functions */\n'
                     '$govuk-assets-path: "%(static_url)s%(app_name)s/";' % dict(
                         static_url=self.static_url,
                         app_name=self.govuk_template_app,
                     ))]
        if path.startswith('govuk_template_base/'):
            return self.resolve_import(path[20:], self.govuk_template_base_source_path)
        if path.startswith('govuk-frontend/'):
            return self.resolve_import(path[15:], self.govuk_template_source_path)

    def resolve_import(self, path: str, source_path: Path):
        if '/' in path:
            base, path = path.rsplit('/', 1)
            source_path = source_path.joinpath(*base.split('/'))
        if not source_path.is_dir():
            return
        for pattern in self.resolution_patterns:
            candidate = source_path / (pattern % path)
            if candidate.is_file():
                return [(str(candidate), self.load_import(candidate))]

    def load_import(self, path: Path):
        with path.open(mode='rt') as f:
            return f.read() + '\n'

    def compile(self, source_path: Path, dest_path: Path):
        sass.compile(
            dirname=(str(source_path), str(dest_path)),
            include_paths=self.include_paths,
            output_style=self.output_style,
            custom_functions=self.govuk_template_functions(),
            importers=[(0, self.govuk_template_importers)],
        )
