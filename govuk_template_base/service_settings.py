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
    product_name = ''
    localise_product_name = False
    phase = ServicePhase.discovery.name
    header_link_view_name = ''
    header_links = []
    footer_sections = []
    meta_links = []

    def __str__(self):
        return self.name

    @property
    def localised_name(self):
        return gettext(self.name) if self.localise_name else self.name

    @property
    def localised_product_name(self):
        return gettext(self.product_name) if self.localise_product_name else self.name

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
    def has_footer_sections(self):
        return bool(self.footer_sections)

    def get_footer_sections(self):
        return self.footer_sections

    @property
    def has_meta_links(self):
        return bool(self.meta_links)

    def get_meta_links(self):
        return self.meta_links


class BaseServiceLinkSection:
    """
    Provides the interface representing groups of footer links
    """
    name = ''
    localise_name = False
    columns = 1
    links = []

    def __str__(self):
        return self.name

    @property
    def localised_name(self):
        return gettext(self.name) if self.localise_name else self.name

    def get_links(self):
        return self.links


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


def _convert_link_confs(link_confs):
    links = []
    for link_conf in link_confs:
        link = BaseServiceLink()
        for link_key, link_value in link_conf.items():
            setattr(link, link_key, link_value)
        links.append(link)
    return links


def default_settings():
    conf = getattr(settings, 'GOVUK_SERVICE_SETTINGS', {})
    if conf:
        if isinstance(conf, BaseServiceSettings):
            return conf

        service_settings = BaseServiceSettings()
        for settings_key, settings_value in conf.items():
            if settings_key in {'header_links', 'meta_links'}:
                setattr(service_settings, settings_key, _convert_link_confs(settings_value))
            elif settings_key == 'footer_sections':
                sections = []
                for section_conf in settings_value:
                    section = BaseServiceLinkSection()
                    for section_key, section_value in section_conf.items():
                        if section_key == 'links':
                            section.links = _convert_link_confs(section_value)
                        else:
                            setattr(section, section_key, section_value)
                    sections.append(section)
                service_settings.footer_sections = sections
            else:
                setattr(service_settings, settings_key, settings_value)

        settings.GOVUK_SERVICE_SETTINGS = service_settings
        return service_settings

    from govuk_template_base.models import ServiceSettings

    return ServiceSettings.objects.first() or ServiceSettings.objects.create(name=BaseServiceSettings.name)
