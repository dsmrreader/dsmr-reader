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
    list_display = ('com_port', )


@admin.register(RetentionSettings)
class RetentionSettingsAdmin(SingletonModelAdmin):
    list_display = ('data_retention_in_hours', )
    fieldsets = (
        (
            None, {
                'fields': ['data_retention_in_hours'],
                'description': _(
                    'Detailed instructions for configuring data retention can be found here: '
                    '<a href="https://dsmr-reader.readthedocs.io/nl/latest/retention.html">Retention documentation</a>'
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
