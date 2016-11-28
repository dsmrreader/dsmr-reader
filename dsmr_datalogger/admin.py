from django.contrib.admin.filters import DateFieldListFilter
from django.contrib import admin
from solo.admin import SingletonModelAdmin

from dsmr_backend.mixins import ReadOnlyAdminModel
from .models.settings import DataloggerSettings
from .models.reading import DsmrReading, MeterStatistics


@admin.register(DataloggerSettings)
class DataloggerSettingsAdmin(SingletonModelAdmin):
    list_display = ('com_port', )


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
