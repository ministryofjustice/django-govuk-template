from pathlib import Path

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BaseAppConfig(AppConfig):
    @property
    def source_path(self):
        return Path(self.path) / 'static-src' / self.name

    @property
    def static_path(self):
        return Path(self.path) / 'static' / self.name


class TemplateAppConfig(BaseAppConfig):
    name = 'govuk_template_base'
    verbose_name = _('GOV.UK Base Template')
