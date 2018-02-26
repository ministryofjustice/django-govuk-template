import importlib
import os
import sys
import warnings

from setuptools import find_packages, setup

if sys.version_info[0:2] < (3, 5):
    warnings.warn('This package will only run on Python version 3.5+')

root_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_path, 'README.rst')) as readme:
    README = readme.read()

package_info = importlib.import_module('govuk_template_base')
setup_extensions = importlib.import_module('govuk_template_base.setup_extensions')

setup_requires = ['setuptools', 'pip', 'wheel']
install_requires = ['django>=1.11']
extras_require = {
    'forms': ['django-govuk-forms'],
    'scss': ['libsass'],
    'watch': ['watchdog'],
}
tests_require = ['flake8']
setup_requires += install_requires

setup(
    name='django-govuk-template',
    version=package_info.__version__,
    author=package_info.__author__,
    url='https://github.com/ministryofjustice/django-govuk-template',
    packages=find_packages(exclude=['demo', 'tests']),
    include_package_data=True,
    license='MIT',
    description='Django app that builds `template` and `elements` components from '
                'the Government Digital Services style guide',
    long_description=README,
    keywords='django govuk template elements frontend toolkit',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    cmdclass=setup_extensions.command_classes,
    setup_requires=setup_requires,
    install_requires=install_requires,
    extras_require=extras_require,
    tests_require=tests_require,
    test_suite='tests',
)
