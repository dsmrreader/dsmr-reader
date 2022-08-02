from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class EnergySupplierPriceForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = EnergySupplierPrice

    def clean_electricity_delivered_1_price(self):
        self._validate_price_defined_for_range("electricity_delivered_1_price")
        return self.cleaned_data.get("electricity_delivered_1_price")

    def clean_electricity_delivered_2_price(self):
        self._validate_price_defined_for_range("electricity_delivered_2_price")
        return self.cleaned_data.get("electricity_delivered_2_price")

    def clean_electricity_returned_1_price(self):
        self._validate_price_defined_for_range("electricity_returned_1_price")
        return self.cleaned_data.get("electricity_returned_1_price")

    def clean_electricity_returned_2_price(self):
        self._validate_price_defined_for_range("electricity_returned_2_price")
        return self.cleaned_data.get("electricity_returned_2_price")

    def clean_gas_price(self):
        self._validate_price_defined_for_range("gas_price")
        return self.cleaned_data.get("gas_price")

    def clean_fixed_daily_cost(self):
        self._validate_price_defined_for_range("fixed_daily_cost")
        return self.cleaned_data.get("fixed_daily_cost")

    def _validate_price_defined_for_range(self, field_name):
        # Skip empty (or zeroed) fields in form.
        if not self.cleaned_data.get(field_name):
            return

        current_start = self.cleaned_data.get("start")
        current_end = self.cleaned_data.get("end")

        if current_start is None or current_end is None:
            raise forms.ValidationError(_("Please fix contract start/end first"))

        existing_contracts = EnergySupplierPrice.objects.exclude(
            # Not do block ourselves.
            pk=self.instance.pk
        ).filter(
            Q(start__lte=current_start, end__gte=current_start)
            | Q(start__lte=current_end, end__gte=current_end)
        )

        if not existing_contracts:
            return

        for current_existing_contract in existing_contracts:
            # Skip zeroed fields in existing contract.
            if getattr(current_existing_contract, field_name) == 0:
                continue

            raise forms.ValidationError(
                _(
                    "This price is already set by another contract within a colliding date range ({} / {}): {}".format(
                        current_existing_contract.start,
                        current_existing_contract.end,
                        current_existing_contract.description,
                    )
                )
            )
