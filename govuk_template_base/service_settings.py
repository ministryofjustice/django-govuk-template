import enum

from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse, NoReverseMatch
from django.utils.translation import gettext, gettext_lazy as _, pgettext_lazy


def view_name_validator(view_name):
    try:
        reverse(view_name)
    except NoReverseMatch:
        raise ValidationError(_('View not found'), code='no_reverse_match')


class ServicePhase(enum.Enum):
    discovery = pgettext_lazy('Service phase', 'Discovery')
    alpha = pgettext_lazy('Service phase', 'Alpha')
    beta = pgettext_lazy('Service phase', 'Beta')
    live = pgettext_lazy('Service phase', 'Live')

    @classmethod
    def model_choices(cls):
        return tuple((item.name, item.value) for item in cls)


class BaseServiceSettings:
    """
    Provides the interface representing the service’s title, phase and header/footer links
    """
    name = 'Untitled service'
    localise_name = False
    phase = ServicePhase.discovery.name
    header_link_view_name = ''
    header_links = []
    footer_links = []

    def __str__(self):
        return self.name

    @property
    def localised_name(self):
        return gettext(self.name) if self.localise_name else self.name

    @property
    def phase_name(self):
        return ServicePhase[self.phase].value

    @property
    def header_link_url(self):
        if self.header_link_view_name:
            return reverse(self.header_link_view_name)
        return self.header_link_view_name

    @property
    def has_header_links(self):
        return bool(self.header_links)

    def get_header_links(self):
        return self.header_links

    @property
    def has_footer_links(self):
        return bool(self.footer_links)

    def get_footer_links(self):
        return self.footer_links


class BaseServiceLink:
    """
    Provides the interface representing a header/footer link
    """
    name = ''
    localise_name = False
    link = ''
    link_is_view_name = False

    def __str__(self):
        return self.name

    @property
    def localised_name(self):
        return gettext(self.name) if self.localise_name else self.name

    @property
    def url(self):
        if self.link_is_view_name:
            return reverse(self.link)
        return self.link


def default_settings():
    conf = getattr(settings, 'GOVUK_SERVICE_SETTINGS', {})
    if conf:
        link_keys = {'header_links', 'footer_links'}
        service_settings = BaseServiceSettings()
        for settings_key, settings_value in conf.items():
            if settings_key in link_keys:
                links = []
                for link_conf in settings_value:
                    link = BaseServiceLink()
                    for link_key, link_value in link_conf.items():
                        setattr(link, link_key, link_value)
                    links.append(link)
                setattr(service_settings, settings_key, links)
            else:
                setattr(service_settings, settings_key, settings_value)
        return service_settings

    from govuk_template_base.models import ServiceSettings

    return ServiceSettings.objects.first() or ServiceSettings.objects.create(name=BaseServiceSettings.name)
