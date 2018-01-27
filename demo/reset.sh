#!/usr/bin/env bash

echo Resetting demo app
cd `dirname $0`
rm db.sqlite  # remove DB
rm -rf govuk_template/ static/  # remove old build files
./manage.py startgovukapp govuk_template  # download and build components
./manage.py migrate  # setup db
./manage.py buildscss  # to create all css
./manage.py collectstatic --no-input  # collect built static assets
./manage.py shell --command "
from govuk_template_base.models import ServiceSettings, Link
service_settings = ServiceSettings.default_settings()
service_settings.name = 'Demo service'
service_settings.phase = 'alpha'
service_settings.header_link_view_name = 'demo:demo'
service_settings.header_links.add(Link.objects.create(name='Home', link='demo:demo', link_is_view_name=True))
service_settings.header_links.add(Link.objects.create(name='GOV.UK', link='https://gov.uk/'))
service_settings.footer_links.add(Link.objects.create(name='Home', link='demo:demo', link_is_view_name=True))
service_settings.footer_links.add(Link.objects.create(name='GOV.UK', link='https://gov.uk/'))
service_settings.save()
"
