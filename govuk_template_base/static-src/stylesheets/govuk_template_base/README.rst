``govuk_template_base/defaults`` is a virtual include that contains some necessary variables.
If using ``buildscss`` management command include this snippet in all base stylesheets importing GOV.UK styles
so that image/asset paths are correctly set. Otherwise set ``$path`` to the images static assets path.

.. code-block:: scss

    @import 'govuk_template_base/defaults';
    // or
    $path: '/static/images/';  // use absolute path
