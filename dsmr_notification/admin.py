from django.contrib import admin

from solo.admin import SingletonModelAdmin

from dsmr_notification.models.settings import NotificationSetting


@admin.register(NotificationSetting)
class NotificationSettingsAdmin(SingletonModelAdmin):
    pass
