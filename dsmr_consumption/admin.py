from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models.settings import ConsumptionSettings
from .models.energysupplier import EnergySupplierPrice


@admin.register(ConsumptionSettings)
class ConsumptionSettingsAdmin(SingletonModelAdmin):
    list_display = ('compactor_grouping_type', )


@admin.register(EnergySupplierPrice)
class EnergySupplierPriceAdmin(admin.ModelAdmin):
    list_display = ('description', 'start', 'end')
