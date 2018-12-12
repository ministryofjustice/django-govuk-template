from django.contrib import admin

from govuk_template_base.models import ServiceSettings, Link, LinkSection


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(LinkSection)
class LinkSectionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(ServiceSettings)
class ServiceSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'phase')
