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
                'fields': ['export', 'upload_interval', 'upload_delay'],
                'description': _(
                    'Implements the following API call: '
                    '<a href="https://pvoutput.org/help.html#api-addstatus" target="_blank">Add Status Service</a>'
                )
            }
        ),
        (
            _('PVOutput Donators'), {
                'fields': ['processing_delay'],
                'description': _(
                    'This feature is ONLY available when you have a DONATOR account for PVOutput.org. '
                    'For more information see: '
                    '<a href="https://pvoutput.org/donate.jsp" target="_blank">Donating to PVOutput</a> '
                    ' and <a href="https://pvoutput.org/help.html#donations" target="_blank">Bonus Features</a>.'
                )
            }
        ),
        (
            _('Automatic fields'), {
                'fields': ['next_export']
            }
        ),
    )
