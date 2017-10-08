from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_pvoutput.models.settings import PVOutputAPISettings, PVOutputAddStatusSettings


@admin.register(PVOutputAPISettings)
class PVOutputAPISettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(PVOutputAddStatusSettings)
class PVOutputAddStatusSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ['next_export']
    fieldsets = (
        (
            None, {
                'fields': ['export', 'upload_interval', 'upload_delay', 'processing_delay', 'next_export'],
                'description': _(
                    'Implements the following API call: https://pvoutput.org/help.html#api-addstatus'
                )
            }
        ),
    )
