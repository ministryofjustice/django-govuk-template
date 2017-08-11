DEMO
====

This is a demo app used for development and testing, it's not included in the distribution.

.. code-block:: python

    rm -rf govuk_template/  # remove old build files
    ./manage.py startgovukapp govuk_template  # download and build components
    ./manage.py migrate  # just in case
    ./manage.py runserver  # see the demo in action
