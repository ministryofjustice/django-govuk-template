import json
import os
from pathlib import Path
import shutil

from django.core.management import CommandError
from django.core.management.commands.startapp import Command as StartAppCommand


class Command(StartAppCommand):
    help = 'Creates an app that can be used as a basis for GOV.UK-styled apps ' \
           'in the current directory or optionally in the given directory.'

    def info_message(self, message, **kwargs):
        if self.verbosity >= 1:
            self.stdout.write(message, **kwargs)

    def debug_message(self, message, **kwargs):
        if self.verbosity >= 2:
            self.stdout.write(message, **kwargs)

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--govuk-template-version', default='0.22.3',
                            help='Choose a specific GOV.UK template version to download')
        parser.add_argument('--govuk-elements-version', default='3.1.1',
                            help='Choose a specific GOV.UK elements version to download')
        parser.add_argument('--govuk-frontend-toolkit-version', default='6.0.4',
                            help='Choose a specific GOV.UK frontend-toolkit version to download')

    def copy_dir(self, src_dir: Path, dest_dir: Path, overwrite=True):
        if not src_dir.is_dir():
            raise FileNotFoundError('%s is not a directory' % src_dir)
        if not dest_dir.is_dir():
            if dest_dir.exists():
                raise FileExistsError('%s is not a directory' % dest_dir)
            dest_dir.mkdir(parents=True)
        for item in src_dir.iterdir():
            dest_file = dest_dir / item.name
            if item.is_dir():
                self.copy_dir(item, dest_file, overwrite=overwrite)
            elif not dest_file.exists() or overwrite:
                self.debug_message('Copying file %s into target app' % dest_file)
                shutil.copy(str(item), str(dest_file))

    def handle(self, **options):
        app_name, target = options.get('name'), options.get('directory') or os.getcwd()
        template_version = options.pop('govuk_template_version')
        elements_version = options.pop('govuk_elements_version')
        frontend_toolkit_version = options.pop('govuk_frontend_toolkit_version')

        options['template'] = str(Path(__file__).parent / 'govuk_template_base')
        super().handle(**options)

        app_dir = Path(target) / app_name
        templates_dir = app_dir / 'templates'
        # static assets all have absolute paths so cannot include app_name
        static_dir = app_dir / 'static'
        images_dir = static_dir / 'images'
        css_dir = static_dir / 'stylesheets'
        source_dir = app_dir / 'static-src'
        scss_dir = source_dir / 'stylesheets'

        for path in (scss_dir, images_dir, css_dir):
            path.is_dir() or path.mkdir(parents=True)

        self.load_govuk_template(template_version, static_dir, templates_dir)
        self.load_govuk_elements(elements_version, frontend_toolkit_version, scss_dir)
        self.load_govuk_frontend_toolkit(frontend_toolkit_version, scss_dir, images_dir)

        self.info_message('Add `%s` to INSTALLED_APPS' % options['name'])
        self.info_message('Add `govuk_template_base.context_processors.govuk_template_base` to '
                          'template context processors')

        self.build_scss(scss_dir, css_dir)

    def load_govuk_template(self, version, static_dir: Path, templates_dir: Path):
        self.info_message('Downloading `govuk_template` version %s' % version)
        archive = self.download(
            'https://github.com/alphagov/govuk_template/releases/download/v%s/django_govuk_template-%s.tgz' % (
                version, version,
            )
        )
        temporary_folder = Path(self.extract(archive))
        self.copy_dir(temporary_folder / 'govuk_template' / 'static', static_dir)
        self.copy_dir(temporary_folder / 'govuk_template' / 'templates' / 'govuk_template', templates_dir)

        self.fix_templates(templates_dir)

    def fix_templates(self, templates_dir: Path):
        for path in templates_dir.rglob('*.html'):
            with path.open('rt') as f:
                text = f.read()
            text = text.replace('{% load staticfiles %}', '{% load static %}')
            with path.open('wt') as f:
                f.write(text)

    def load_govuk_elements(self, elements_version, frontend_toolkit_version, scss_dir: Path):
        self.debug_message('Loading `govuk-elements-sass` package listing')
        with open(self.download('https://registry.npmjs.org/govuk-elements-sass/')) as f:
            elements_package = json.load(f)

        try:
            elements_dist = elements_package['versions'][elements_version]
        except KeyError:
            raise CommandError('`govuk-elements-sass` version %s not available, choose from: %s' % (
                elements_version, ', '.join(elements_package['versions'].keys())
            ))
        try:
            frontend_toolkit_dependency = elements_dist['dependencies']['govuk_frontend_toolkit']
            self.info_message('Check that `govuk_frontend_toolkit` version "%s" is compatible '
                              'with `govuk-elements-sass` dependency of "%s"' % (
                                  frontend_toolkit_version, frontend_toolkit_dependency
                              ))
        except KeyError:
            raise CommandError('`govuk_frontend_toolkit` dependency not found, is it no longer needed?')
        other_dependencies = set(elements_dist.get('dependencies', {}).keys()) - {'govuk_frontend_toolkit'}
        if other_dependencies:
            self.stderr.write('`govuk-elements-sass` now has additional dependencies that are not handled: %s' % (
                ', '.join(sorted(other_dependencies)),
            ))
        self.info_message('Downloading `govuk-elements-sass` version %s' % elements_version)
        archive = self.download(elements_dist['dist']['tarball'])
        temporary_folder = Path(self.extract(archive))
        self.copy_dir(temporary_folder / 'public' / 'sass', scss_dir)

    def load_govuk_frontend_toolkit(self, frontend_toolkit_version, scss_dir: Path, images_dir: Path):
        self.debug_message('Loading `govuk_frontend_toolkit` package listing')
        with open(self.download('https://registry.npmjs.org/govuk_frontend_toolkit/')) as f:
            frontend_toolkit_package = json.load(f)

        try:
            frontend_toolkit_dist = frontend_toolkit_package['versions'][frontend_toolkit_version]
        except KeyError:
            raise CommandError('`govuk_frontend_toolkit` version %s not available, choose from: %s' % (
                frontend_toolkit_version, ', '.join(frontend_toolkit_package['versions'].keys())
            ))
        self.info_message('Downloading `govuk_frontend_toolkit` version %s' % frontend_toolkit_version)
        archive = self.download(frontend_toolkit_dist['dist']['tarball'])
        temporary_folder = Path(self.extract(archive))
        self.copy_dir(temporary_folder / 'stylesheets', scss_dir)
        self.copy_dir(temporary_folder / 'images', images_dir)

    def build_scss(self, scss_dir: Path, css_dir: Path):
        try:
            import sass
        except ImportError:
            sass = None

        if not sass:
            self.info_message('libsass is not available, try installing using [scss] extra')
            return

        sass.compile(dirname=(str(scss_dir), str(css_dir)), output_style='compressed')
