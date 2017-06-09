from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class TemplateAppConfig(AppConfig):
    name = 'govuk_template'
    verbose_name = _('GOV.UK Template Builder')
