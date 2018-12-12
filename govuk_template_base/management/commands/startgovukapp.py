import json
import os
from pathlib import Path
import shutil

from django.conf import settings
from django.core.management import CommandError
from django.core.management.commands.startapp import Command as StartAppCommand

GOVUK_FRONTEND_VERSION = '2.4.1'


class Command(StartAppCommand):
    help = 'Creates an app that can be used as a basis for GOV.UK-styled apps ' \
           'in the current directory or optionally in the given directory.'
    rewrite_template_suffixes = StartAppCommand.rewrite_template_suffixes + (
        ('.scss-tpl', '.scss'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.paths_to_remove = []

    def info_message(self, message, **kwargs):
        if self.verbosity >= 1:
            self.stdout.write(message, **kwargs)

    def debug_message(self, message, **kwargs):
        if self.verbosity >= 2:
            self.stdout.write(message, **kwargs)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--govuk-frontend-version', default=GOVUK_FRONTEND_VERSION,
                            help='Choose a specific GOV.UK frontend version to download')

    def copy_dir(self, src_dir: Path, dest_dir: Path, overwrite=True, path_filter=None):
        if not src_dir.is_dir():
            raise FileNotFoundError('%s is not a directory' % src_dir)
        if not dest_dir.is_dir():
            if dest_dir.exists():
                raise FileExistsError('%s is not a directory' % dest_dir)
            dest_dir.mkdir(parents=True)
        for item in filter(path_filter, src_dir.iterdir()):
            dest_file = dest_dir / item.name
            if item.is_dir():
                self.copy_dir(item, dest_file, overwrite=overwrite, path_filter=path_filter)
            elif not dest_file.exists() or overwrite:
                self.debug_message('Copying file %s into target app' % dest_file)
                shutil.copy(str(item), str(dest_file))

    def handle(self, **options):
        app_name, target = options.get('name'), options.get('directory') or os.getcwd()
        frontend_version = options.pop('govuk_frontend_version')

        static_url = getattr(settings, 'STATIC_URL', None) or '/static/'
        if not static_url.endswith('/'):
            static_url += '/'

        options['extensions'].append('scss')
        options['template'] = str(Path(__file__).parent / 'govuk_template')
        options['static_url'] = static_url

        super().handle(**options)

        self.paths_to_remove = []

        app_dir = Path(target) / app_name
        templates_dir = app_dir / 'templates' / app_name
        source_dir = app_dir / 'static-src' / app_name
        static_dir = app_dir / 'static' / app_name

        for path in (templates_dir, source_dir, static_dir):
            path.is_dir() or path.mkdir(parents=True)

        try:
            self.load_govuk_frontend(frontend_version, source_dir, static_dir)
            self.process_templates(app_name, templates_dir)
            self.build_scss(app_name, source_dir, static_dir)

            message_context = {'app_name': options['name']}
            self.info_message('Add `%(app_name)s` to INSTALLED_APPS setting' % message_context,
                              style_func=self.style.SUCCESS)
            self.info_message('Add `%(app_name)s.context_processors.%(app_name)s` to '
                              'template context processors' % message_context,
                              style_func=self.style.SUCCESS)
        finally:
            self.cleanup()

    def load_govuk_frontend(self, version: str, source_dir: Path, static_dir: Path):
        self.debug_message('Loading `govuk_frontend` package listing')
        with open(self.download('https://registry.npmjs.org/govuk-frontend/')) as f:
            frontend_package = json.load(f)
        try:
            elements_dist = frontend_package['versions'][version]
        except KeyError:
            raise CommandError('`govuk-frontend` version %s not available, choose from: %s' % (
                version, ', '.join(sorted(frontend_package['versions'].keys()))
            ))

        self.info_message('Downloading `govuk_frontend` version %s' % version)
        archive = self.download(elements_dist['dist']['tarball'])
        temporary_dir = Path(self.extract(archive))
        temporary_assets_dir = temporary_dir / 'assets'

        # copy images and fonts
        self.copy_dir(temporary_assets_dir, static_dir)

        # copy javascript files
        self.copy_dir(
            temporary_dir, source_dir,
            path_filter=lambda path: path != temporary_assets_dir and path.is_dir() or path.suffix.lower() == '.js'
        )
        (static_dir / 'base.js').symlink_to(source_dir / 'all.js')

        # copy sass files
        self.copy_dir(
            temporary_dir, source_dir,
            path_filter=lambda path: path != temporary_assets_dir and path.is_dir() or path.suffix.lower() == '.scss'
        )
        (source_dir / 'all.scss').rename(source_dir / '_all.scss')
        (source_dir / 'all-ie8.scss').rename(source_dir / '_all-ie8.scss')

    def process_templates(self, app_name: str, templates_dir: Path):
        for path in templates_dir.rglob('*.html'):
            with path.open('rt') as f:
                text = f.read()
            text = text.replace('##app_name##', app_name)
            with path.open('wt') as f:
                f.write(text)

    def build_scss(self, app_name: str, scss_dir: Path, css_dir: Path):
        from govuk_template_base.management.commands.buildscss import Compiler

        try:
            compiler = Compiler(govuk_template_app=app_name, govuk_template_source_path=scss_dir)
            compiler.compile(scss_dir, css_dir)
        except CommandError as e:
            self.info_message(str(e), style_func=self.style.WARNING)

    def cleanup(self):
        if self.paths_to_remove:
            self.debug_message('Cleaning up temporary files')
            for path_to_remove in self.paths_to_remove:
                if os.path.isfile(path_to_remove):
                    os.remove(path_to_remove)
                else:
                    shutil.rmtree(path_to_remove)
