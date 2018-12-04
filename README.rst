Django GOV.UK Template
======================

**This library has not yet been updated to use the new** `Design system`_

It should be easy to make a Django-based service that follows Government Digital Services’ style guide and reference materials.
But https://pypi.python.org/pypi/govuk-template is not kept updated and is not readily usable in Django and
https://github.com/alphagov/govuk_template cannot be installed directly into a Django project without complex build steps.

This package takes components published by GDS and creates an app in a Django project which can then be used as normal.
This process downloads a release from https://github.com/alphagov/govuk_template and the contents of Node.js packages
https://www.npmjs.com/package/govuk-elements-sass and https://www.npmjs.com/package/govuk_frontend_toolkit

NB: Until version 1.0, there is likely going to be a lot of variation in the api, so it’s a good idea to pin a specific minor version.

Usage
-----

Install with pip, i.e. ``pip install django-govuk-template``. There are 3 optional extras that can also be installed:

- ``forms``: also installs ``django-govuk-forms`` which outputs Django forms using the correct HTML structures for GOV.UK standard styles
- ``scss``: allows building SCSS assets with a management command
- ``watch``: use in combination with the ``scss`` extra to automatically build SCSS assets while developing locally

Django project setup
~~~~~~~~~~~~~~~~~~~~

- Setup a Django project using ``manage.py startproject`` or other means
- Install ``django-govuk-template`` (along with desired extras) and add ``govuk_template_base`` to ``INSTALLED_APPS``
- Call ``manage.py startgovukapp [[app name, e.g. govuk_template]]``
    - Add this app to ``INSTALLED_APPS``
    - Ensure that this app is included in source control as the intention is that it’s only rebuilt as needed
    - If an update is needed in the future, delete the app created in previous step and run this command again
- Add ``govuk_template_base.context_processors.govuk_template_base`` to the template context processors
- Use ``[[app name, e.g. govuk_template]].html`` as the template to extend from and overrive the ``inner_content`` block

See the demo folder in this repository on `GitHub`_, it is not included in distributions.

Another demo [1]_ shows the process of converting the Django tutorial polls app – see the commit history.

Service settings
~~~~~~~~~~~~~~~~

The service’s title, phase and header/footer links can be configured through service settings objects.

Typically, these are stored in the ``ServiceSettings`` model and initial configuration could be a data migration or a fixture.
However if the ``GOVUK_SERVICE_SETTINGS`` setting is defined, it will take precedence. This is useful in cases where no database is set up.

.. code-block:: python

    GOVUK_SERVICE_SETTINGS = {
        'name': 'Service name',
        'phase': 'beta',
        'header_link_view_name': 'service_app:home',
        'header_links': [
            {'name': 'Home', 'link': 'service_app:home', 'link_is_view_name': True},
        ],
    }

Service settings stored in models allow for localisation into different languages.
Set ``localise_name`` to ``True`` and provide translations in your project’s localised messages.

Development
-----------

.. image:: https://travis-ci.org/ministryofjustice/django-govuk-template.svg?branch=master
    :target: https://travis-ci.org/ministryofjustice/django-govuk-template

Please report bugs and open pull requests on `GitHub`_.

Use ``python setup.py test`` to run all tests.

This repository does not need to be updated for every release of GDS’s packages, only breaking changes for overridden components may need fixes.

If any localisable strings change, run ``python setup.py makemessages compilemessages``.

Distribute a new version to `PyPi`_ by updating the ``VERSION`` tuple in ``govuk_template_base`` and run ``python setup.py compilemessages sdist bdist_wheel upload``.

To do
-----

- Add browser-sync/equivalent for easier local development
- Add javascript building options
- Add additional GOV.UK patterns
- Improve service setting configuration
- Perhaps improve SCSS building mechanism (e.g. command line fallback) and print styles
- Perhaps improve app naming or documentation regarding ``govuk_template_base`` and ``govuk_template``
- It would be nice to require as few external tools as possible (e.g. docker/node/ruby) to make building simpler

Copyright
---------

Copyright (C) 2018 HM Government (Ministry of Justice Digital Services).
See LICENSE.txt for further details.

.. _Design system: https://design-system.service.gov.uk/
.. _GitHub: https://github.com/ministryofjustice/django-govuk-template
.. _PyPi: https://pypi.org/project/django-govuk-template/

.. [1] https://github.com/ministryofjustice/gov.uk-with-django
