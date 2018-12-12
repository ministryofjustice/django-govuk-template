import django.core.validators
from django.db import migrations, models

import govuk_template_base.service_settings


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('localise_name', models.BooleanField(default=False, verbose_name='Localise name')),
                ('link', models.CharField(max_length=255, verbose_name='Link')),
                ('link_is_view_name', models.BooleanField(default=False, verbose_name='Link is a view name')),
            ],
            options={
                'ordering': ('modified',),
                'verbose_name': 'Link',
                'verbose_name_plural': 'Links',
            },
        ),
        migrations.CreateModel(
            name='LinkSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('localise_name', models.BooleanField(default=False, verbose_name='Localise name')),
                ('columns', models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('links', models.ManyToManyField(blank=True, related_name='_linksection_links_+', to='govuk_template_base.Link', verbose_name='Links')),
            ],
            options={
                'verbose_name': 'Link section',
                'verbose_name_plural': 'Link sections',
                'ordering': ('-modified',),
            },
            bases=(govuk_template_base.service_settings.BaseServiceLinkSection, models.Model),
        ),
        migrations.CreateModel(
            name='ServiceSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('localise_name', models.BooleanField(default=False, verbose_name='Localise name')),
                ('product_name', models.CharField(max_length=100, blank=True, verbose_name='Product name')),
                ('localise_product_name', models.BooleanField(default=False, verbose_name='Localise product name')),
                ('phase', models.CharField(choices=[('discovery', 'Discovery'), ('alpha', 'Alpha'), ('beta', 'Beta'), ('live', 'Live')], default='discovery', max_length=10, verbose_name='Phase')),
                ('header_link_view_name', models.CharField(blank=True, max_length=100, validators=[govuk_template_base.service_settings.view_name_validator], verbose_name='View name')),
                ('meta_links', models.ManyToManyField(blank=True, related_name='_servicesettings_meta_links_+', to='govuk_template_base.Link', verbose_name='Footer meta links')),
                ('meta_text', models.CharField(blank=True, max_length=255)),
                ('footer_sections', models.ManyToManyField(blank=True, to='govuk_template_base.LinkSection', verbose_name='Footer sections')),
                ('header_links', models.ManyToManyField(blank=True, related_name='_servicesettings_header_links_+', to='govuk_template_base.Link', verbose_name='Header links')),
            ],
            options={
                'ordering': ('-modified',),
                'verbose_name_plural': 'Service settings',
                'verbose_name': 'Service settings',
            },
        ),
    ]
