from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _


class EnergySupplierPriceManager(models.Manager):
    def by_date(self, target_date):
        """ Selects the energy prices price paid for a date. """
        return self.get_queryset().get(
            # This comes in handy when you have no contract end (yet).
            Q(end__gte=target_date) | Q(end__isnull=True),
            start__lte=target_date,
        )


class EnergySupplierPrice(models.Model):
    """
    Represents the price you are/were charged by your energy supplier.
    Prices are per unit, which is either one kWh power or m3 gas.
    """
    class Meta:
        unique_together = ('start', 'end')

    objects = EnergySupplierPriceManager()

    start = models.DateField()
    end = models.DateField(null=True, blank=True)
    description = models.CharField(
        max_length=255, null=True, blank=True,
        help_text=_('For your own reference, i.e. your supplier name')
    )
    electricity_1_price = models.DecimalField(max_digits=11, decimal_places=5)
    electricity_2_price = models.DecimalField(max_digits=11, decimal_places=5)
    gas_price = models.DecimalField(max_digits=11, decimal_places=5)

    def __str__(self):
        return self.description or 'Energy Supplier'
