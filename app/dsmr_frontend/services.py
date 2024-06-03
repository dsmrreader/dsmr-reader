import struct
from typing import Optional, Any

from django.utils import translation
from django.utils.translation import gettext as _
from django.utils import formats
from django.utils import timezone

from dsmr_frontend.models.message import Notification


def hex_color_to_rgb(hex_color: str) -> Any:
    """
    Converts a hex color string to an RGB list.
    Thanks to: http://stackoverflow.com/a/4296263/5905550
    """
    hex_color = hex_color.replace("#", "")

    return struct.unpack("BBB", bytes.fromhex(hex_color))


def get_translated_string(text: str, language: str = "nl") -> str:
    """Forces translation of a string in a language."""
    # Credits to: http://www.technomancy.org/python/django-i18n-manually-turn-on-a-language/
    old_lang = translation.get_language()

    translation.activate(language)
    translated_text = _(text)
    translation.activate(old_lang)

    return translated_text


def display_dashboard_message(message: str, redirect_to: Optional[str] = None) -> None:
    """Displays a message with today's date on the dashboard, but prevents any UNREAD duplicates."""
    today = formats.date_format(timezone.localtime(timezone.now()).date())
    Notification.objects.get_or_create(
        message="{}: {}".format(today, message), redirect_to=redirect_to, read=False
    )
