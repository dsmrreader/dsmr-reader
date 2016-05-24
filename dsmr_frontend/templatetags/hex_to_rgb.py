from django.template.defaultfilters import stringfilter
from django import template

import dsmr_frontend.services


register = template.Library()


@register.filter(name='hex_to_rgb')
@stringfilter
def hex_to_rgb(value):
    rgb = dsmr_frontend.services.hex_color_to_rgb(hex_color=value)
    return ', '.join(str(v) for v in rgb)
