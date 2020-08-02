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
from .models.statistics import MeterStatistics


@admin.register(DataloggerSettings)
class DataloggerSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('restart_required',)
    fieldsets = (
        (
            _('Input method and DSMR protocol'), {
                'fields': ['input_method', 'dsmr_version'],
                'description': _(
                    'The datalogger process should automatically restart to apply changes. To manually restart, '
                    'see the <a href="https://dsmr-reader.readthedocs.io/nl/v4/faq/restart_processes.html">FAQ</a>.'
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
                'fields': ['process_sleep', 'log_telegrams'],
            }
        ),
        (
            _('System'), {
                'fields': [
                    'restart_required'
                ],
                'description': _(
                    'The datalogger process should automatically restart to apply changes. To manually restart, '
                    'see the <a href="https://dsmr-reader.readthedocs.io/nl/v4/faq/restart_processes.html">FAQ</a>.'
                )
            }
        ),
    )


@admin.register(RetentionSettings)
class RetentionSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['data_retention_in_hours'],
                'description': _(
                    'Retention policy applies to telegrams and related data that is no longer needed after processing.'
                )
            }
        ),
    )


@admin.register(DsmrReading)
class DsmrReadingAdmin(ReadOnlyAdminModel):
    """ Read only model. """
    ordering = ['-timestamp']
    list_display = ('timestamp', 'electricity_currently_delivered', 'electricity_currently_returned')
    list_filter = (
        ('timestamp', DateTimeRangeFilter),
    )


@admin.register(MeterStatistics)
class MeterStatisticsAdmin(ReadOnlyAdminModel):
    """ Read only model. """
    list_display = ('timestamp', 'electricity_tariff', 'power_failure_count')


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
