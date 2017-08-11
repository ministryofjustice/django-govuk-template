from django.conf import settings
from django.utils.translation import get_language, gettext


def govuk_template_base(_):
    html_lang = get_language()
    return {
        'html_lang': html_lang or settings.LANGUAGE_CODE,
        'skip_link_message': gettext('Skip to main content'),
        'logo_link_title': gettext('Go to the GOV.UK homepage'),
        'crown_copyright_message': gettext('© Crown copyright'),
    }
