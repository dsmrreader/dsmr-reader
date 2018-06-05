from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_notification.models.settings import NotificationSetting, StatusNotificationSetting


@admin.register(NotificationSetting)
class NotificationSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('next_notification', )
    fieldsets = (
        (None, {
            'fields': ['notification_service', 'next_notification'],
            'description': _(
                'Detailed instructions for configuring notifications can be found here: '
                '<a href="https://dsmr-reader.readthedocs.io/nl/latest/faq.html#usage-notification-daily-usage-'
                'statistics-on-your-smartphone">FAQ in documentation</a>'
            )
        }),
        ('Pushover', {
            'fields': ['pushover_api_key', 'pushover_user_key'],
            'description': _('Only applies when using Pushover')
        }),
        ('Prowl', {
            'fields': ['prowl_api_key'],
            'description': _('Only applies when using Prowl')
        }),
    )


@admin.register(StatusNotificationSetting)
class StatusNotificationSettingAdmin(SingletonModelAdmin):
    readonly_fields = ('next_check', )
    fieldsets = (
        (
            None, {
                'fields': ['next_check'],
                'description': _(
                    'System checks for sending status notifications when the datalogger is lagging behind.'
                )
            }
        ),
    )
