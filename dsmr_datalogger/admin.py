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
    fieldsets = (
        (
            _('Protocol'), {
                'fields': ['dsmr_version'],
                'description': _(
                    'Note: You might have to restart the "dsmr_datalogger" process for any changes to apply. '
                    'See the <a href="https://dsmr-reader.readthedocs.io/nl/v4/faq/restart_processes.html">FAQ</a>.'
                )
            }
        ),
        (
            _('Advanced'), {
                'fields': ['com_port', 'process_sleep'],
                'description': _(
                    'Note: You will have to restart the "dsmr_datalogger" process for any changes to apply. '
                    'See the <a href="https://dsmr-reader.readthedocs.io/nl/v4/faq/restart_processes.html">FAQ</a>.'
                )
            }
        ),
        (
            _('Debugging'), {
                'fields': ['log_telegrams'],
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
                    'Detailed instructions for configuring data retention can be found here: '
                    '<a href="https://dsmr-reader.readthedocs.io/nl/v4/admin/datalogger.html">Documentation</a>'
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
