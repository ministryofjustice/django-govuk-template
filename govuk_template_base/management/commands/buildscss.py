import os
import textwrap

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_labels', nargs='*',
                            help='Limit SCSS building to these apps.')
        parser.add_argument('--collect', action='store_true',
                            help='Save output CSS in collected static files location.')

    def handle(self, *app_labels, **options):
        if app_labels:
            try:
                app_configs = [apps.get_app_config(app_label) for app_label in app_labels]
            except (LookupError, ImportError) as e:
                raise CommandError('%s. Are you sure your INSTALLED_APPS setting is correct?' % e)
        else:
            app_configs = apps.get_app_configs()
        verbosity = options['verbosity']
        collected_dest = options['collect'] and os.path.join(settings.STATIC_ROOT, 'stylesheets')
        paths = (os.path.join(app_config.path, 'static-src', 'stylesheets') for app_config in app_configs)
        paths = list(filter(os.path.isdir, paths))
        for source_path in paths:
            dest_path = collected_dest or os.path.join(source_path, os.pardir, os.pardir, 'static', 'stylesheets')
            if verbosity > 1:
                self.stdout.write('Compiling SCSS files in %s' % source_path)
            compile_scss(source_path, dest_path, include_paths=paths)


def scss_defaults_importer(path):
    if path == 'govuk_template_base/defaults':
        static_url = getattr(settings, 'STATIC_URL', None) or '/static/'
        if not static_url.endswith('/'):
            static_url += '/'
        return [(path, textwrap.dedent('''
            // Image asset paths required by GOV.UK frontend toolkit functions
            $path: '%(static_url)simages/';
        ''' % dict(static_url=static_url)))]


def compile_scss(source_path, dest_path, include_paths=(), output_style='compressed'):
    try:
        import sass
    except ImportError:
        raise CommandError('libsass is not available, try installing using [scss] extra')
    sass.compile(dirname=(source_path, dest_path), include_paths=include_paths,
                 output_style=output_style,
                 importers=[(0, scss_defaults_importer)])
