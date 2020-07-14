from django.contrib import admin
from solo.admin import SingletonModelAdmin

from dsmr_client.models import ContinuousClientSettings


@admin.register(ContinuousClientSettings)
class ContinuousClientSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['process_sleep'],
            }
        ),
    )
