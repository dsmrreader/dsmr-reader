from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _


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
    objects = EnergySupplierPriceManager()

    start = models.DateField(
        verbose_name=_('Start'), help_text=_('Contract start')
    )
    end = models.DateField(
        null=True, blank=True, verbose_name=_('End'), help_text=_('Contract end')
    )
    description = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_('Description'),
        help_text=_('For your own reference, i.e. the name of your supplier')
    )
    electricity_1_price = models.DecimalField(
        max_digits=11, decimal_places=5, default=0, verbose_name=_('Electricity 1 price')
    )
    electricity_2_price = models.DecimalField(
        max_digits=11, decimal_places=5, default=0, verbose_name=_('Electricity 2 price')
    )
    gas_price = models.DecimalField(
        max_digits=11, decimal_places=5, default=0, verbose_name=_('Gas price')
    )

    def __str__(self):
        return self.description or 'Energy Supplier'

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Energy supplier price')
        verbose_name_plural = _('Energy supplier prices')
        unique_together = ('start', 'end')
