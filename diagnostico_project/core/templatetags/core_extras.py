import re

from django import template

register = template.Library()


@register.filter
def get_active(url, section):
    section_regex = re.compile(r'^/.*/')
    search = section_regex.search(url)
    if search is not None:
        if search.group(0) == '/{}/'.format(section):
            return 'active'
    return ''
