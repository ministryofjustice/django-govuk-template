from django.core.validators import MinValueValidator, URLValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from govuk_template_base.service_settings import BaseServiceLink, BaseServiceLinkSection, BaseServiceSettings, \
    ServicePhase, view_name_validator


class ServiceSettings(BaseServiceSettings, models.Model):
    """
    Defines the service’s title, phase and header/footer links
    """
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    localise_name = models.BooleanField(verbose_name=_('Localise name'), default=BaseServiceSettings.localise_name)
    product_name = models.CharField(verbose_name=_('Product name'), max_length=100, blank=True)
    localise_product_name = models.BooleanField(verbose_name=_('Localise product name'),
                                                default=BaseServiceSettings.localise_product_name)
    phase = models.CharField(verbose_name=_('Phase'), max_length=10,
                             choices=ServicePhase.model_choices(), default=BaseServiceSettings.phase)
    header_link_view_name = models.CharField(verbose_name=_('View name'), max_length=100,
                                             blank=True, validators=[view_name_validator])
    header_links = models.ManyToManyField('Link', verbose_name=_('Header links'), blank=True, related_name='+')
    footer_sections = models.ManyToManyField('LinkSection', verbose_name=_('Footer sections'), blank=True)
    meta_links = models.ManyToManyField('Link', verbose_name=_('Footer meta links'), blank=True, related_name='+')
    meta_text = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ('-modified',)
        verbose_name = verbose_name_plural = _('Service settings')

    @property
    def has_header_links(self):
        return self.header_links.exists()

    def get_header_links(self):
        yield from self.header_links.all()

    @property
    def has_footer_sections(self):
        return self.footer_sections.exists()

    def get_footer_sections(self):
        return self.footer_sections.all()

    @property
    def has_meta_links(self):
        return self.meta_links.exists()

    def get_meta_links(self):
        yield from self.meta_links.all()


class LinkSection(BaseServiceLinkSection, models.Model):
    """
    Defines a group of footer links
    """
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    localise_name = models.BooleanField(verbose_name=_('Localise name'), default=BaseServiceSettings.localise_name)
    columns = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)])
    links = models.ManyToManyField('Link', verbose_name=_('Links'), blank=True, related_name='+')

    class Meta:
        ordering = ('-modified',)
        verbose_name = _('Link section')
        verbose_name_plural = _('Link sections')

    def get_links(self):
        return self.links.all()


class Link(BaseServiceLink, models.Model):
    """
    Defines a header/footer link
    """
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name=_('Name'), max_length=255)
    localise_name = models.BooleanField(verbose_name=_('Localise name'), default=BaseServiceLink.localise_name)
    link = models.CharField(verbose_name=_('Link'), max_length=255)
    link_is_view_name = models.BooleanField(verbose_name=_('Link is a view name'),
                                            default=BaseServiceLink.link_is_view_name)

    class Meta:
        ordering = ('modified',)
        verbose_name = _('Link')
        verbose_name_plural = _('Links')

    def clean(self):
        if self.link_is_view_name:
            view_name_validator(self.link)
        else:
            URLValidator(schemes=('http', 'https'))(self.link)
