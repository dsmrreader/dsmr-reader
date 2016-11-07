from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class NotificationSetting(SingletonModel):
    NOTIFICATION_NMA = 'nma'
    NOTIFICATION_PROWL = 'prowl'

    NOTIFICATION_CHOICES = (
        (NOTIFICATION_NMA, _('NotifyMyAndroid')),
        (NOTIFICATION_PROWL, _('Prowl')),
    )

    NOTIFICATION_API_URL = {
        NOTIFICATION_NMA: 'https://www.notifymyandroid.com/publicapi/notify',
        NOTIFICATION_PROWL: 'https://api.prowlapp.com/publicapi/add'
    }

    send_notification = models.BooleanField(
        default=False,
        verbose_name=_('Send notification'),
        help_text=_(
            'Whether or not you want to receive a notification of your '
            'daily usage on your smartphone'
        )
    )
    notification_service = models.CharField(
        max_length=20,
        choices=NOTIFICATION_CHOICES,
        default=NOTIFICATION_NMA,
        verbose_name=_('Notification service'),
        help_text=_(
            'Which notification service to use for sending daily '
            'usage notifications'
        )
    )
    api_key = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        default=None,
        verbose_name=_('Notification service API key'),
        help_text=_(
            'The API key used send messages to your smartphone. '
            'Please visit https://notifymyandroid.com/ or '
            'https://www.prowlapp.com/ to download and use the apps.'
        )
    )
    next_notification = models.DateField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Next notification'),
        help_text=_(
            'Timestamp of the next notification. Managed by application.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Notification configuration')
