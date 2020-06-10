from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_notification.models.settings import NotificationSetting, StatusNotificationSetting


@admin.register(NotificationSetting)
class NotificationSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('next_notification', )
    fieldsets = (
        (None, {
            'fields': ['notification_service'],
            'description': _(
                'Detailed instructions for configuring notifications can be found here: '
                '<a href="https://dsmr-reader.readthedocs.io/nl/v4/admin/notifications.html">Documentation</a>'
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
        ('Telegram', {
            'fields': ['telegram_api_key', 'telegram_chat_id'],
            'description': _('Only applies when using your own Telegram bot')
        }),
        (
            _('Automatic fields'), {
                'fields': ['next_notification']
            }
        ),
    )


@admin.register(StatusNotificationSetting)
class StatusNotificationSettingAdmin(SingletonModelAdmin):
    readonly_fields = ('next_check', )
    fieldsets = (
        (
            _('Automatic fields'), {
                'fields': ['next_check'],
                'description': _(
                    'System checks for sending status notifications when the datalogger is lagging behind.'
                )
            }
        ),
    )
