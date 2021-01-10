from django.conf import settings
from django.contrib import admin
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin
from rangefilter.filter import DateTimeRangeFilter
import django.db.models.signals

from dsmr_backend.mixins import ReadOnlyAdminModel
from dsmr_backend.models.schedule import ScheduledProcess
from .models.settings import DataloggerSettings, RetentionSettings
from .models.reading import DsmrReading
from .models.statistics import MeterStatistics, MeterStatisticsChange


@admin.register(DataloggerSettings)
class DataloggerSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_datalogger/datalogger_settings/change_form.html'
    readonly_fields = ('restart_required',)
    fieldsets = (
        (
            _('Input method and DSMR protocol'), {
                'fields': ['input_method', 'dsmr_version'],
                'description': _(
                    'The datalogger process should automatically restart to apply changes. To manually restart, '
                    'see the <a href="https://dsmr-reader.readthedocs.io/nl/v4/faq.html">FAQ</a>.'
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
                    'The datalogger process should automatically restart to apply changes. To manually restart, '
                    'see the <a href="https://dsmr-reader.readthedocs.io/nl/v4/faq.html">FAQ</a>.'
                )
            }
        ),
    )


@admin.register(RetentionSettings)
class RetentionSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_datalogger/retention_settings/change_form.html'
    list_display = ('data_retention_in_hours', )


@admin.register(DsmrReading)
class DsmrReadingAdmin(ReadOnlyAdminModel):
    ordering = ['-timestamp']
    list_display = ('timestamp', 'processed', 'electricity_currently_delivered', 'electricity_currently_returned')
    list_filter = (
        ('timestamp', DateTimeRangeFilter),
    )


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
