Django GOV.UK Template
======================

**🚨 Breaking change: versions 0.9 and above are completely incompatible with 0.1 to 0.8.**

It should be easy to make a Django-based service that follows Government Digital Services’ style guide and reference materials.

The official `Design System`_ allows for 2 mechanisms of usage:

- Running your service in a NodeJS environment and taking advantage of choosing and customising components as needed [1]_
- Installing pre-built asset files into ``/assets/`` of your site and writing all HTML templates yourself [2]_

This package takes an in-between approach by allowing you to customise the build step and including some minimal HTML templates.
It works by downloading a specific version of the NodeJS package and converting it into a new app inside your Django project.

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
- Install ``django-govuk-template`` (along with desired extras) and add ``govuk_template_base`` to ``INSTALLED_APPS`` in your settings
- Call ``manage.py startgovukapp [[app name, e.g. govuk_template]]``
    - Add this app to ``INSTALLED_APPS`` setting
    - Ensure that this app is included in source control as the intention is that it’s only rebuilt as needed
    - If an update is needed in the future, delete the app created in this step and run this command again
- Add ``[[app name, e.g. govuk_template]].context_processors.[[app name, e.g. govuk_template]]`` to the template context processors
- Use ``[[app name, e.g. govuk_template]]/base.html`` as the base template to extend from and overrive the ``inner_content`` block

See the demo folder in this repository on `GitHub`_, it is not included in distributions.

Another demo [3]_ shows the process of converting the Django tutorial polls app – see the commit history.

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

This repository does not need to be updated for every release of GDS’s packages,
only breaking changes for overridden components may need fixes.

If any localisable strings change, run ``python setup.py makemessages compilemessages``.

Distribute a new version to `PyPi`_ by updating the ``VERSION`` tuple in ``govuk_template_base``
and run ``python setup.py compilemessages sdist bdist_wheel upload``.

To do
-----

- Perhaps improve app naming or documentation regarding ``govuk_template_base`` and ``govuk_template_base``
- Improve service setting configuration
- Perhaps improve SCSS building mechanism (e.g. command line fallback) and print styles
- Add more HTML component templates
- Add javascript building options
- Add additional GOV.UK patterns
- Add browser-sync/equivalent for easier local development
- It would be nice to require as few external tools as possible (e.g. docker/node/ruby) to make building simpler

Copyright
---------

Copyright (C) 2018 HM Government (Ministry of Justice Digital and Technology).
See LICENSE.txt for further details.

.. _Design System: https://design-system.service.gov.uk/
.. _GitHub: https://github.com/ministryofjustice/django-govuk-template
.. _PyPi: https://pypi.org/project/django-govuk-template/

.. [1] https://design-system.service.gov.uk/get-started/production/#option-1-install-using-npm
.. [2] https://design-system.service.gov.uk/get-started/production/#option-2-include-compiled-files
.. [3] https://github.com/ministryofjustice/gov.uk-with-django
