import distutils.log
import os

import setuptools


class SimpleCommand(setuptools.Command):
    user_options = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        cwd = os.getcwd()
        os.chdir(os.path.dirname(__file__))
        self.run_command()
        os.chdir(cwd)

    def run_command(self):
        raise NotImplementedError


class MakeMessages(SimpleCommand):
    description = 'update localisation messages files'

    def run_command(self):
        from django.core.management import call_command

        self.announce('Updating localisation message files', level=distutils.log.INFO)
        call_command('makemessages', all=True, no_wrap=True, keep_pot=True)


class CompileMessages(SimpleCommand):
    description = 'compile localisation messages files'

    def run_command(self):
        from django.core.management import call_command

        self.announce('Compiling localisation message files', level=distutils.log.INFO)
        call_command('compilemessages', fuzzy=False)


command_classes = {
    'makemessages': MakeMessages,
    'compilemessages': CompileMessages,
}
