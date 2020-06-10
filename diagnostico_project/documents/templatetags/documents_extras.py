import re

from django import template

register = template.Library()


@register.filter
def clean_filename(value):
    return re.sub(r'.*/.*/', '', str(value))
