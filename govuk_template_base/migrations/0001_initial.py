from django.db import migrations, models
import govuk_template_base.models


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
            name='ServiceSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('localise_name', models.BooleanField(default=False, verbose_name='Localise name')),
                ('phase', models.CharField(choices=[('discovery', 'Discovery'), ('alpha', 'Alpha'), ('beta', 'Beta'), ('live', 'Live')], default='discovery', max_length=10, verbose_name='Phase')),
                ('header_link_view_name', models.CharField(blank=True, max_length=100, validators=[govuk_template_base.models.view_name_validator], verbose_name='View name')),
                ('footer_links', models.ManyToManyField(blank=True, related_name='_servicesettings_footer_links_+', to='govuk_template_base.Link', verbose_name='Footer links')),
                ('header_links', models.ManyToManyField(blank=True, related_name='_servicesettings_header_links_+', to='govuk_template_base.Link', verbose_name='Header links')),
            ],
            options={
                'ordering': ('-modified',),
                'verbose_name_plural': 'Service settings',
                'verbose_name': 'Service settings',
            },
        ),
    ]
