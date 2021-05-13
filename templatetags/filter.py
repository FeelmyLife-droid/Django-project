from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name='split')
@stringfilter
def slpit_filter(value: str, arg):

    return value.split(arg)[1]
