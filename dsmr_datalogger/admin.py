from django.contrib.admin.filters import DateFieldListFilter
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_backend.mixins import ReadOnlyAdminModel
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
                    'See the <a href="https://dsmr-reader.readthedocs.io/nl/v2/faq/restart_processes.html">FAQ</a>.'
                )
            }
        ),
        (
            _('Advanced'), {
                'fields': ['com_port', 'process_sleep'],
                'description': _(
                    'Note: You will have to restart the "dsmr_datalogger" process for any changes to apply. '
                    'See the <a href="https://dsmr-reader.readthedocs.io/nl/v2/faq/restart_processes.html">FAQ</a>.'
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
                    'Detailed instructions for configuring data retention can be found here: '
                    '<a href="https://dsmr-reader.readthedocs.io/nl/v2/admin/datalogger.html">Documentation</a>'
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
        ('timestamp', DateFieldListFilter),
    )


@admin.register(MeterStatistics)
class MeterStatisticsAdmin(ReadOnlyAdminModel):
    """ Read only model. """
    list_display = ('timestamp', 'electricity_tariff', 'power_failure_count')
