import enum

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.db import models
from django.urls import NoReverseMatch, reverse
from django.utils.translation import gettext, gettext_lazy as _, pgettext_lazy


class ServicePhase(enum.Enum):
    discovery = pgettext_lazy('Service phase', 'Discovery')
    alpha = pgettext_lazy('Service phase', 'Alpha')
    beta = pgettext_lazy('Service phase', 'Beta')
    live = pgettext_lazy('Service phase', 'Live')

    @classmethod
    def model_choices(cls):
        return tuple((item.name, item.value) for item in cls)


def view_name_validator(view_name):
    try:
        reverse(view_name)
    except NoReverseMatch:
        raise ValidationError(_('View not found'), code='no_reverse_match')


class ServiceSettings(models.Model):
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name=_('Name'), max_length=100)
    localise_name = models.BooleanField(verbose_name=_('Localise name'), default=False)
    phase = models.CharField(verbose_name=_('Phase'), max_length=10,
                             choices=ServicePhase.model_choices(), default=ServicePhase.discovery.name)
    header_link_view_name = models.CharField(verbose_name=_('View name'), max_length=100,
                                             blank=True, validators=[view_name_validator])
    header_links = models.ManyToManyField('Link', verbose_name=_('Header links'), blank=True, related_name='+')
    footer_links = models.ManyToManyField('Link', verbose_name=_('Footer links'), blank=True, related_name='+')

    class Meta:
        ordering = ('-modified',)
        verbose_name = verbose_name_plural = _('Service settings')

    def __str__(self):
        return self.name

    @classmethod
    def default_settings(cls):
        return cls.objects.first() or cls.objects.create(name='Untitled')

    @property
    def localised_name(self):
        return gettext(self.name) if self.localise_name else self.name

    @property
    def header_link_url(self):
        if self.header_link_view_name:
            return reverse(self.header_link_view_name)
        return self.header_link_view_name

    @property
    def phase_name(self):
        return ServicePhase[self.phase].value

    @property
    def has_header_links(self):
        return self.header_links.exists()

    @property
    def has_footer_links(self):
        return self.footer_links.exists()


class Link(models.Model):
    modified = models.DateTimeField(auto_now=True)
    name = models.CharField(verbose_name=_('Name'), max_length=255)
    localise_name = models.BooleanField(verbose_name=_('Localise name'), default=False)
    link = models.CharField(verbose_name=_('Link'), max_length=255)
    link_is_view_name = models.BooleanField(verbose_name=_('Link is a view name'), default=False)

    class Meta:
        ordering = ('modified',)
        verbose_name = _('Link')
        verbose_name_plural = _('Links')

    def __str__(self):
        return self.name

    def clean(self):
        if self.link_is_view_name:
            view_name_validator(self.link)
        else:
            URLValidator(schemes=('http', 'https'))(self.link)

    @property
    def localised_name(self):
        return gettext(self.name) if self.localise_name else self.name

    @property
    def url(self):
        if self.link_is_view_name:
            return reverse(self.link)
        return self.link
