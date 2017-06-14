import json
import os
from pathlib import Path
import shutil

from django.core.management import CommandError
from django.core.management.commands.startapp import Command as StartAppCommand


class Command(StartAppCommand):
    help = 'Creates an app that can be used as a basis for GOV.UK-styled apps ' \
           'in the current directory or optionally in the given directory.'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument('--govuk-template-version', dest='govuk_template_version',
                            default='0.19.2',
                            help='Choose a specific GOV.UK template version to download')
        parser.add_argument('--govuk-elements-version', dest='govuk_elements_version',
                            default='3.0.3',
                            help='Choose a specific GOV.UK elements version to download')

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
                if self.verbosity >= 2:
                    self.stdout.write('Copying file %s into target app' % dest_file)
                shutil.copy(str(item), str(dest_file))

    def handle(self, **options):
        app_name, target = options.get('name'), options.get('directory') or os.getcwd()
        govuk_template_version = options.pop('govuk_template_version')
        govuk_elements_version = options.pop('govuk_elements_version')

        options['template'] = str(Path(__file__).parent / 'govuk_base_template')
        super().handle(**options)

        app_dir = Path(target) / app_name
        static_dir = app_dir / 'static' / app_name  # TODO: remove app_name here because styles expect no parent dir
        static_source_dir = app_dir / 'static-src' / app_name
        templates_dir = app_dir / 'templates' / app_name

        self.load_govuk_template(govuk_template_version, static_dir, templates_dir)
        self.load_govuk_elements(govuk_elements_version, static_dir, static_source_dir)

        if self.verbosity >= 1:
            self.stdout.write('Created GOV.UK base app, add `%s` to INSTALLED_APPS' % options['name'])

    def load_govuk_template(self, version, static_dir: Path, templates_dir: Path):
        if self.verbosity >= 1:
            self.stdout.write('Downloading `govuk_template` version %s' % version)
        archive = self.download(
            'https://github.com/alphagov/govuk_template/releases/download/v%s/django_govuk_template-%s.tgz' % (
                version, version,
            )
        )
        temporary_folder = Path(self.extract(archive))
        self.copy_dir(temporary_folder / 'govuk_template' / 'static', static_dir)
        self.copy_dir(temporary_folder / 'govuk_template' / 'templates' / 'govuk_template', templates_dir)

    def load_govuk_elements(self, elements_version, static_dir: Path, static_source_dir: Path):
        scss_dir = static_source_dir / 'stylesheets'
        if not scss_dir.is_dir():
            scss_dir.mkdir(parents=True)
        images_dir = static_dir / 'images'
        if not images_dir.is_dir():
            images_dir.mkdir(parents=True)

        if self.verbosity >= 2:
            self.stdout.write('Loading `govuk-elements-sass` package listing')
        with open(self.download('https://registry.npmjs.org/govuk-elements-sass/')) as f:
            elements_package = json.load(f)
        if self.verbosity >= 2:
            self.stdout.write('Loading `govuk_frontend_toolkit` package listing')
        with open(self.download('https://registry.npmjs.org/govuk_frontend_toolkit/')) as f:
            frontend_toolkit_package = json.load(f)

        try:
            # get the exact version as specified from options
            elements_dist = elements_package['versions'][elements_version]
        except KeyError:
            raise CommandError('`govuk-elements-sass` version %s not available, choose from: %s' % (
                elements_version, ', '.join(elements_package['versions'].keys())
            ))
        if self.verbosity >= 1:
            self.stdout.write('Downloading `govuk-elements-sass` version %s' % elements_version)
        archive = self.download(elements_dist['dist']['tarball'])
        temporary_folder = Path(self.extract(archive))
        self.copy_dir(temporary_folder / 'public' / 'sass', scss_dir)

        other_dependencies = set(elements_dist['dependencies'].keys()) - {'govuk_frontend_toolkit'}
        if other_dependencies:
            self.stderr.write('`govuk-elements-sass` now has additional dependencies that are not handled: %s' % (
                ', '.join(sorted(other_dependencies)),
            ))
        try:
            frontend_toolkit_dependency = elements_dist['dependencies']['govuk_frontend_toolkit']
        except KeyError:
            raise CommandError('`govuk_frontend_toolkit` dependency not found, is it no longer needed?')
        frontend_toolkit_version = Range(frontend_toolkit_dependency).highest_version(
            frontend_toolkit_package['versions'].keys()
        )
        frontend_toolkit_dist = frontend_toolkit_package['versions'][frontend_toolkit_version]
        if self.verbosity >= 1:
            self.stdout.write('Downloading `govuk-elements-sass` version %s' % frontend_toolkit_version)
        archive = self.download(frontend_toolkit_dist['dist']['tarball'])
        temporary_folder = Path(self.extract(archive))
        self.copy_dir(temporary_folder / 'stylesheets', scss_dir)
        self.copy_dir(temporary_folder / 'images', images_dir)
