``govuk_template_base/settings`` is a virtual include that contains some necessary variables.

If using ``buildscss`` management command include this snippet in all base stylesheets importing GOV.UK styles
so that asset paths are correctly set. Otherwise set ``$govuk-assets-path`` to the images static assets path.

.. code-block:: scss

    @import 'govuk_template_base/settings';
    // or
    $govuk-assets-path: '/static/govuk_template/' !default;  // NB: use absolute path

Additionally, ``buildscss`` provides two SASS functions:

- ``django-static`` for linking to static assets
- ``django-media`` for linking to uploaded media
