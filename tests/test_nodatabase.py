import unittest
import django


class NoDatabaseTestCase(unittest.TestCase):
    def setUp(self):
        from django.conf import settings
        settings.configure(
            DEBUG=True,
            LOGGING_CONFIG=None,
            GOVUK_TEMPLATE_NO_DATABASE=True,
            MIGRATION_MODULES={'govuk_template_base': None},
            SERVICE_SETTINGS={
                'localised_name': 'Test Service',
                'phase': 'beta',
                'phase_name': 'Beta',
                'has_header_links': True,
                'header_link_url': 'http://www.testservice.gov.uk/',
                'header_links': {
                    'all': [
                        {
                            'url': 'https://www.testservice.gov.uk/header1',
                            'localised_name': 'Header link 1'
                        }
                    ]
                },
                'has_footer_links': True,
                'footer_links': {
                    'all': [
                        {
                            'url': 'https://www.testservice.gov.uk/footer1',
                            'localised_name': 'Footer link 1'
                        }
                    ]
                }
            },
            INSTALLED_APPS=('govuk_template_base',)
        )
        django.setup()

    def test_no_database(self):
        from govuk_template_base.templatetags import govuk_template_base
        service_settings = govuk_template_base.get_service_settings()
        self.assertEqual(service_settings['localised_name'], 'Test Service')
        self.assertEqual(service_settings['phase'], 'beta')
        self.assertEqual(service_settings['phase_name'], 'Beta')
        self.assertEqual(service_settings['has_header_links'], True)
