from django.contrib import admin
from solo.admin import SingletonModelAdmin

from dsmr_backend.mixins import ReadOnlyAdminModel
from .models.consumption import ElectricityConsumption, GasConsumption
from .models.energysupplier import EnergySupplierPrice
from .models.settings import ConsumptionSettings


@admin.register(ConsumptionSettings)
class ConsumptionSettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(EnergySupplierPrice)
class EnergySupplierPriceAdmin(admin.ModelAdmin):
    list_display = ('description', 'start', 'end')


@admin.register(ElectricityConsumption)
class ElectricityConsumptionAdmin(ReadOnlyAdminModel):
    list_display = ('read_at', 'currently_delivered', 'currently_returned')


@admin.register(GasConsumption)
class GasConsumptionAdmin(ReadOnlyAdminModel):
    list_display = ('read_at', 'currently_delivered')
