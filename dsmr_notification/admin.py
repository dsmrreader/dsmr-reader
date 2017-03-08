from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_notification.models.settings import NotificationSetting


@admin.register(NotificationSetting)
class NotificationSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('next_notification', )
    fieldsets = (
        (
            None, {
                'fields': ['send_notification', 'notification_service', 'api_key', 'next_notification'],
                'description': _(
                    'Detailed instructions for configuring notifications can be found here: '
                    '<a href="https://dsmr-reader.readthedocs.io/nl/latest/faq.html#usage-notification-daily-usage-'
                    'statistics-on-your-smartphone">FAQ in documentation</a>'
                )
            }
        ),
    )
