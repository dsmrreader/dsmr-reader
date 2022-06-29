from django.utils import formats, timezone
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from rangefilter.filters import DateTimeRangeFilter
from solo.admin import SingletonModelAdmin

from dsmr_backend.mixins import DeletionOnlyAdminModel
from .forms import EnergySupplierPriceForm
from .models.consumption import ElectricityConsumption, GasConsumption, QuarterHourPeakElectricityConsumption
from .models.energysupplier import EnergySupplierPrice
from .models.settings import ConsumptionSettings


@admin.register(ConsumptionSettings)
class ConsumptionSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_consumption/consumption_settings/change_form.html'


@admin.register(EnergySupplierPrice)
class EnergySupplierPriceAdmin(admin.ModelAdmin):
    save_on_top = True
    save_as = True
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
                'description': _(
                    'Note that the meaning of each tariff may differ among countries. For Dutch users: Tariff 1 is '
                    'known as the <strong>low tariff</strong> and tariff 2 as the <strong>high tariff</strong>.'
                ),
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
class ElectricityConsumptionAdmin(DeletionOnlyAdminModel):
    save_on_top = True
    list_filter = (
        ('read_at', DateTimeRangeFilter),
    )
    list_display = ('read_at', 'currently_delivered', 'currently_returned')


@admin.register(GasConsumption)
class GasConsumptionAdmin(DeletionOnlyAdminModel):
    save_on_top = True
    list_filter = (
        ('read_at', DateTimeRangeFilter),
    )
    list_display = ('read_at', 'currently_delivered')


@admin.register(QuarterHourPeakElectricityConsumption)
class QuarterHourPeakElectricityConsumptionAdmin(DeletionOnlyAdminModel):
    list_display = ('average_delivered', 'duration', 'read_at_start_formatted', 'read_at_end_formatted')
    ordering = ('-read_at_start', 'average_delivered')  # Latest on top
    list_filter = (
        ('read_at_start', DateTimeRangeFilter),
    )

    def read_at_start_formatted(self, obj):
        return formats.date_format(timezone.localtime(obj.read_at_start), 'DSMR_VERBOSE_DATETIME_FORMAT')

    def read_at_end_formatted(self, obj):
        return formats.date_format(timezone.localtime(obj.read_at_end), 'DSMR_VERBOSE_DATETIME_FORMAT')

    read_at_start_formatted.short_description = _('Start')  # type: ignore[attr-defined]
    read_at_end_formatted.short_description = _('End')  # type: ignore[attr-defined]
