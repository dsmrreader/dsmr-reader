from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from rangefilter.filter import DateTimeRangeFilter
from solo.admin import SingletonModelAdmin

from dsmr_backend.mixins import ReadOnlyAdminModel
from .forms import EnergySupplierPriceForm
from .models.consumption import ElectricityConsumption, GasConsumption
from .models.energysupplier import EnergySupplierPrice
from .models.settings import ConsumptionSettings


@admin.register(ConsumptionSettings)
class ConsumptionSettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(EnergySupplierPrice)
class EnergySupplierPriceAdmin(admin.ModelAdmin):
    change_form_template = 'dsmr_consumption/energy_supplier_prices/change_form.html'
    list_display = ('description', 'start', 'end')
    form = EnergySupplierPriceForm
    fieldsets = (
        (
            None, {
                'fields': ['start', 'end', 'description'],
            }
        ),
        (
            _('Electricity'), {
                'fields': ['electricity_delivered_1_price', 'electricity_delivered_2_price',
                           'electricity_returned_1_price', 'electricity_returned_2_price'],
            }
        ),
        (
            _('Gas'), {
                'fields': ['gas_price'],
            }
        ),
        (
            _('Fixed costs'), {
                'fields': ['fixed_daily_cost'],
            }
        ),
    )


@admin.register(ElectricityConsumption)
class ElectricityConsumptionAdmin(ReadOnlyAdminModel):
    list_filter = (
        ('read_at', DateTimeRangeFilter),
    )
    list_display = ('read_at', 'currently_delivered', 'currently_returned')


@admin.register(GasConsumption)
class GasConsumptionAdmin(ReadOnlyAdminModel):
    list_filter = (
        ('read_at', DateTimeRangeFilter),
    )
    list_display = ('read_at', 'currently_delivered')
