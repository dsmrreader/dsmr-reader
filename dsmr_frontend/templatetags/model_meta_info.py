from django import template
register = template.Library()


@register.simple_tag
def model_meta_info(instance, field, meta):
    return getattr(instance._meta.get_field(field), meta).title().capitalize()
