import subprocess
import unittest


class CodeStyleTestCase(unittest.TestCase):
    def test_code_style(self):
        try:
            subprocess.check_output(['flake8'])
        except subprocess.CalledProcessError as e:
            self.fail('Code style checks failed\n\n%s' % e.output.decode('utf-8'))
