NAME?
=====

Things to name:
- this package: can't be template/govuk-template
    - a django app (likely of same name) and needs to be included in INSTALLED_APPS of project
    - makes a django app (project owner decides) in project by downloading and compiling gov.uk toolkits

Motivation
----------

It should be easy to make a Django-based service that follows Government Digital Services’ style guide and reference materials.
It would be nice to not need many external tools installed to build static assets.

- https://pypi.python.org/pypi/govuk-template is not kept up to date
- https://github.com/alphagov/govuk_template cannot be installed directly into a Django project without complex build steps
- hence download Django release from https://github.com/alphagov/govuk_template/releases and build custom app in the target Django project
- this repo does not need to be updated for every release, only breaking changes for overridden components

-

Usage
-----

Install using ``pip install govuk-django-template``. Sample usage:

.. code-block:: python

    ???

Development
-----------

Please report bugs and open pull requests on `GitHub`_.

Use ``python setup.py test`` to run all tests.

Distribute a new version by updating the ``VERSION`` tuple in ``govuk_django_template`` and run ``python setup.py sdist bdist_wheel upload``.

Copyright
---------

Copyright |copy| 2017 HM Government (Ministry of Justice Digital Services). See LICENSE.txt for further details.

.. |copy| unicode:: 0xA9 .. copyright symbol
.. _GitHub: https://github.com/ministryofjustice/govuk-django-template
