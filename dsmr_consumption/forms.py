from django import forms
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class EnergySupplierPriceForm(forms.ModelForm):
    class Meta:
        exclude = []
        model = EnergySupplierPrice

    def clean(self):
        """ Ensure there is no overlap in existing contracts. """
        current_start = self.cleaned_data.get('start')
        current_end = self.cleaned_data.get('end')

        existing = EnergySupplierPrice.objects.exclude(
            # Not do block ourselves.
            pk=self.instance.pk
        ).filter(
            Q(
                start__lte=current_start,
                end__gte=current_start
            ) | Q(
                start__lte=current_end,
                end__gte=current_end
            )
        )

        if not existing:
            return

        raise forms.ValidationError(_(
            'At least one other contract collides with this date range: {} ({} - {})'.format(
                existing[0].description,
                existing[0].start,
                existing[0].end
            )
        ))
