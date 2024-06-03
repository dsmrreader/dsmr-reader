from django.utils.translation import gettext_lazy as _
from django.db import models
from solo.models import SingletonModel


class NotificationSetting(SingletonModel):
    PUSHOVER_API_URL = "https://api.pushover.net/1/messages.json"
    PROWL_API_URL = "https://api.prowlapp.com/publicapi/add"
    TELEGRAM_API_URL = "https://api.telegram.org/bot"

    NOTIFICATION_NONE = None
    NOTIFICATION_DUMMY = "dummy"
    NOTIFICATION_PROWL = "prowl"
    NOTIFICATION_PUSHOVER = "pushover"
    NOTIFICATION_TELEGRAM = "telegram"

    NOTIFICATION_CHOICES = (
        (NOTIFICATION_NONE, _("--- Disabled ---")),
        (NOTIFICATION_DUMMY, _("Dummy (e.g. custom plugin)")),
        (NOTIFICATION_PUSHOVER, _("Pushover")),
        (NOTIFICATION_PROWL, _("Prowl")),
        (NOTIFICATION_TELEGRAM, _("Telegram")),
    )

    notification_service = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        default=None,
        choices=NOTIFICATION_CHOICES,
        verbose_name=_("Notification service"),
        help_text=_(
            "Which notification service to use for sending daily usage notifications"
        ),
    )
    prowl_api_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("API key"),
    )
    pushover_api_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        verbose_name=_("API key"),
        help_text=_("The API key of your Pushover Application"),
    )
    pushover_user_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        help_text=_("Your User Key displayed in your Pushover dashboard"),
    )
    telegram_api_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        help_text=_(
            "Your Telegram bot token. The token looks something like 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
        ),
    )
    telegram_chat_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        help_text=_(
            'Identifier for the target chat ID, or @handle of a channel (without the "@")'
        ),
    )
    next_notification = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Next notification"),
        help_text=_("Timestamp of the next notification. Managed by application."),
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _("Notification Apps configuration")


class StatusNotificationSetting(SingletonModel):
    """Periodic check of the application status at regular intervals. Notifies when something is a miss."""

    next_check = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_("Next check"),
        help_text=_("Timestamp of the next check. Managed by application."),
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _("Status notification configuration")
