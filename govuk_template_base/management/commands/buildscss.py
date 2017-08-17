import os

from django.core.management import BaseCommand, CommandError


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('args', metavar='app_labels', nargs='*', help='Limit SCSS building to these apps.')

    def handle(self, *app_labels, **options):
        try:
            import sass
        except ImportError:
            raise CommandError('libsass is not available, try installing using [scss] extra')
        from django.apps import apps

        if app_labels:
            try:
                app_configs = [apps.get_app_config(app_label) for app_label in app_labels]
            except (LookupError, ImportError) as e:
                raise CommandError('%s. Are you sure your INSTALLED_APPS setting is correct?' % e)
        else:
            app_configs = apps.get_app_configs()
        verbosity = options['verbosity']
        paths = (os.path.join(app_config.path, 'static-src', 'stylesheets') for app_config in app_configs)
        paths = list(filter(os.path.isdir, paths))
        for source_path in paths:
            dest_path = os.path.join(source_path, os.pardir, os.pardir, 'static', 'stylesheets')
            if verbosity > 1:
                self.stdout.write('Compiling SCSS files in %s' % source_path)
            sass.compile(dirname=(source_path, dest_path), include_paths=paths, output_style='compressed')
