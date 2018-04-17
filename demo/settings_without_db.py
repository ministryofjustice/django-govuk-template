from settings import *  # noqa

DATABASES = {}

GOVUK_SERVICE_SETTINGS = {
    'name': 'Demo service',
    'phase': 'alpha',
    'header_link_view_name': 'demo:demo',
    'header_links': [
        {'name': 'Home', 'link': 'demo:demo', 'link_is_view_name': True},
        {'name': 'GOV.UK', 'link': 'https://gov.uk/'},
    ],
    'footer_links': [
        {'name': 'Home', 'link': 'demo:demo', 'link_is_view_name': True},
        {'name': 'GOV.UK', 'link': 'https://gov.uk/'},
    ],
}
