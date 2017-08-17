import itertools

from django import template
from django.utils.translation import gettext_lazy as _

from govuk_template_base.models import ServiceSettings

register = template.Library()


@register.filter
def separate_thousands(value):
    if not isinstance(value, int):
        return value
    return '{:,}'.format(value)


@register.simple_tag
def get_service_settings():
    return ServiceSettings.default_settings()


@register.inclusion_tag('govuk_template_base/page-list.html')
def page_list(page, page_count, query_string=None, end_padding=1, page_padding=2):
    if page_count < 7:
        pages_with_ellipses = range(1, page_count + 1)
    else:
        pages = sorted(set(itertools.chain(
            range(1, end_padding + 2),
            range(page - page_padding, page + page_padding + 1),
            range(page_count - end_padding, page_count + 1),
        )))
        pages_with_ellipses = []
        last_page = 0
        for index in pages:
            if index < 1 or index > page_count:
                continue
            if last_page + 1 < index:
                pages_with_ellipses.append(None)
            pages_with_ellipses.append(index)
            last_page = index
    return {
        'page': page,
        'page_count': page_count,
        'page_range': pages_with_ellipses,
        'query_string': query_string,
    }


@register.inclusion_tag('govuk_template_base/pagination.html')
def pagination(prev_url, next_url, prev_title=None, next_title=None, prev=_('Previous'), next=_('Next')):
    context = {'prev': prev, 'next': next}
    if prev_url:
        context['prev_page'] = {'title': prev_title, 'url': prev_url}
    if next_url:
        context['next_page'] = {'title': next_title, 'url': next_url}
    return context
