Django GOV.UK Template
======================

It should be easy to make a Django-based service that follows Government Digital Services’ style guide and reference materials.
https://pypi.python.org/pypi/govuk-template is not kept updated and is not readily usable in Django.
https://github.com/alphagov/govuk_template cannot be installed directly into a Django project without complex build steps.

This package takes pieces published by GDS and creates an app in a Django project which can then be used as normal.
This process downloads a release from https://github.com/alphagov/govuk_template

Usage
-----

- Setup a Django project using ``manage.py startproject`` or other means
- Install ``django-govuk-template`` and add ``govuk_template_base`` to ``INSTALLED_APPS``
- Call ``manage.py startgovukapp [[app name, e.g. govuk_template]]``
    - Add this app to ``INSTALLED_APPS``
    - Ensure that this app is included in source control as the intention is that it’s only rebuilt as needed
    - If an update is needed in the future, delete the app created in previous step and run this command again

Development
-----------

Please report bugs and open pull requests on `GitHub`_.

Use ``python setup.py test`` to run all tests.

This repository does not need to be updated for every release of GDS’s packages, only breaking changes for overridden components may need fixes.

Distribute a new version by updating the ``VERSION`` tuple in ``govuk_django_template`` and run ``python setup.py sdist bdist_wheel upload``.

To do
-----

- It would be nice to require as few external tools as possible (e.g. docker/node/ruby) to make building simpler

Copyright
---------

Copyright |copy| 2017 HM Government (Ministry of Justice Digital Services). See LICENSE.txt for further details.

.. |copy| unicode:: 0xA9 .. copyright symbol
.. _GitHub: https://github.com/ministryofjustice/django-govuk-template
