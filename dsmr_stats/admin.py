from django.contrib import admin
from django.contrib.auth.models import Group
from solo.admin import SingletonModelAdmin

from .models.energysupplier import EnergySupplierPrice
from .models.note import Note
from .models.settings import StatsSettings


@admin.register(EnergySupplierPrice)
class EnergySupplierPriceAdmin(admin.ModelAdmin):
    list_display = ('description', 'start', 'end')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('day', 'description')


@admin.register(StatsSettings)
class StatsSettingsAdmin(SingletonModelAdmin):
    list_display = ('reverse_dashboard_graphs', )


# Too bad there is no global admin.py, so we'll just disabled Group here.
admin.site.unregister(Group)
