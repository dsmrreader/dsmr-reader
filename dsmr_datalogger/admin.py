from django.conf import settings
from django.contrib import admin
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin
from rangefilter.filters import DateTimeRangeFilter
import django.db.models.signals

from dsmr_backend.mixins import ReadOnlyAdminModel, DeletionOnlyAdminModel
from dsmr_backend.models.schedule import ScheduledProcess
from .models.settings import DataloggerSettings, RetentionSettings
from .models.reading import DsmrReading
from .models.statistics import MeterStatistics, MeterStatisticsChange


@admin.register(DataloggerSettings)
class DataloggerSettingsAdmin(SingletonModelAdmin):
    save_on_top = True
    change_form_template = 'dsmr_datalogger/datalogger_settings/change_form.html'
    readonly_fields = ('restart_required',)
    fieldsets = (
        (
            _('Input method and DSMR protocol'), {
                'fields': ['input_method', 'dsmr_version'],
                'description': _(
                    'The datalogger process should automatically restart to apply changes.'
                )
            }
        ),
        (
            _('When using serial socket input method'), {
                'fields': ['serial_port'],
            }
        ),
        (
            _('When using network socket input method'), {
                'fields': ['network_socket_address', 'network_socket_port'],
            }
        ),
        (
            _('Advanced'), {
                'fields': ['process_sleep', 'override_telegram_timestamp'],
            }
        ),
        (
            _('System'), {
                'fields': [
                    'restart_required'
                ],
                'description': _(
                    'The datalogger process should automatically restart to apply changes.'
                )
            }
        ),
    )


@admin.register(RetentionSettings)
class RetentionSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_datalogger/retention_settings/change_form.html'
    list_display = ('data_retention_in_hours', )


@admin.register(DsmrReading)
class DsmrReadingAdmin(DeletionOnlyAdminModel):
    save_on_top = True
    ordering = ['-timestamp']
    list_display = (
        'timestamp', 'processed', 'formatted_electricity_delivered_1', 'formatted_electricity_delivered_2',
        'formatted_electricity_returned_1', 'formatted_electricity_returned_2', 'formatted_extra_device_delivered'
    )
    list_filter = (
        ('timestamp', DateTimeRangeFilter),
    )

    def formatted_electricity_delivered_1(self, obj: DsmrReading) -> str:  # pragma: no cover
        if not obj.electricity_delivered_1:
            return '-'

        return str(obj.electricity_delivered_1)
    formatted_electricity_delivered_1.short_description = 'electricity 1'  # type: ignore[attr-defined]

    def formatted_electricity_delivered_2(self, obj: DsmrReading) -> str:  # pragma: no cover
        if not obj.electricity_delivered_2:
            return '-'

        return str(obj.electricity_delivered_2)
    formatted_electricity_delivered_2.short_description = 'electricity 2'  # type: ignore[attr-defined]

    def formatted_electricity_returned_1(self, obj: DsmrReading) -> str:  # pragma: no cover
        if not obj.electricity_returned_1:
            return '-'

        return str(obj.electricity_returned_1)
    formatted_electricity_returned_1.short_description = 'electricity returned 1'  # type: ignore[attr-defined]

    def formatted_electricity_returned_2(self, obj: DsmrReading) -> str:  # pragma: no cover
        if not obj.electricity_returned_2:
            return '-'

        return str(obj.electricity_returned_2)
    formatted_electricity_returned_2.short_description = 'electricity returned 2'  # type: ignore[attr-defined]

    def formatted_extra_device_delivered(self, obj: DsmrReading) -> str:  # pragma: no cover
        if not obj.extra_device_delivered:
            return '-'

        return str(obj.extra_device_delivered)
    formatted_extra_device_delivered.short_description = 'gas'  # type: ignore[attr-defined]


@admin.register(MeterStatistics)
class MeterStatisticsAdmin(ReadOnlyAdminModel, SingletonModelAdmin):
    change_form_template = 'dsmr_datalogger/meter_statistics/change_form.html'


@admin.register(MeterStatisticsChange)
class MeterStatisticsChangeAdmin(ReadOnlyAdminModel):
    list_display = ('created_at', 'field', 'old_value', 'new_value')


@receiver(django.db.models.signals.post_save, sender=RetentionSettings)
def handle_retention_settings_update(sender, instance, **kwargs):
    """ Hook to toggle related scheduled process. """
    retention_enabled = instance.data_retention_in_hours != RetentionSettings.RETENTION_NONE
    ScheduledProcess.objects.filter(
        module=settings.DSMRREADER_MODULE_RETENTION_DATA_ROTATION
    ).update(
        planned=timezone.now(),
        active=retention_enabled
    )
