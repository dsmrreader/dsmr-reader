from django.contrib import admin

from dsmr_stats.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.note import Note


@admin.register(EnergySupplierPrice)
class EnergySupplierPriceAdmin(admin.ModelAdmin):
    list_display = ('description', 'start', 'end')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('day', 'description')
