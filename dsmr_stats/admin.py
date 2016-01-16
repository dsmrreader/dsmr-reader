from django.contrib import admin
from django.contrib.auth.models import Group
from solo.admin import SingletonModelAdmin


from dsmr_stats.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.note import Note
from dsmr_stats.models.settings import StatsSettings


@admin.register(EnergySupplierPrice)
class EnergySupplierPriceAdmin(admin.ModelAdmin):
    list_display = ('description', 'start', 'end')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('day', 'description')


@admin.register(StatsSettings)
class StatsSettingsAdmin(SingletonModelAdmin):
    list_display = ('compactor_grouping_type')


# Too bad there is no global admin.py, so we'll just disabled Group here.
admin.site.unregister(Group)
