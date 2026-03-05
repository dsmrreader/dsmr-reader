from django import template
from django.utils.html import format_html
from django.utils.safestring import SafeData


register = template.Library()


@register.filter(is_safe=True)
def decimal_html(value: object) -> SafeData:
    """Splits a decimal number at its separator and wraps the fractional part in a smaller span.

    When both '.' and ',' are present (e.g. thousands separators), the one appearing last
    is treated as the decimal separator (e.g. '35.267,585' → sep=',', '1,234.56' → sep='.').
    """
    text = str(value)
    dot_pos = text.rfind(".")
    comma_pos = text.rfind(",")

    if dot_pos == -1 and comma_pos == -1:
        return format_html("{}", text)

    sep_pos = max(dot_pos, comma_pos)
    sep = text[sep_pos]
    integer_part = text[:sep_pos]
    decimal_part = text[sep_pos + 1 :]
    return format_html('{}<span class="badge-decimal">{}{}</span>', integer_part, sep, decimal_part)
