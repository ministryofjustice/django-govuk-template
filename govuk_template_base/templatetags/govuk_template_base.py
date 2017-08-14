from django import template

from govuk_template_base.models import ServiceSettings

register = template.Library()


@register.simple_tag
def get_service_settings():
    return ServiceSettings.default_settings()
