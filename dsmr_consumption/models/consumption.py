from django.db import models
from django.utils.translation import ugettext_lazy as _


class ElectricityConsumption(models.Model):
    """ Point in time of electricity consumption (usage), extracted from reading(s). """
    read_at = models.DateTimeField(unique=True)
    delivered_1 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter Reading electricity delivered to client (low tariff) in 0,001 kWh")
    )
    returned_1 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter Reading electricity delivered by client (low tariff) in 0,001 kWh")
    )
    delivered_2 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh")
    )
    returned_2 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh")
    )
    currently_delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Actual electricity power delivered (+P) in 1 Watt resolution"),
        db_index=True
    )
    currently_returned = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Actual electricity power received (-P) in 1 Watt resolution"),
        db_index=True
    )
    phase_currently_delivered_l1 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Instantaneous active power L1 (+P) in W resolution"),
        db_index=True
    )
    phase_currently_delivered_l2 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Instantaneous active power L2 (+P) in W resolution"),
        db_index=True
    )
    phase_currently_delivered_l3 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Instantaneous active power L3 (+P) in W resolution"),
        db_index=True
    )

    def __sub__(self, other):
        """ Allows models to be subtracted from each other. """
        data = {}

        for current in ('delivered_1', 'returned_1', 'delivered_2', 'returned_2'):
            data.update({current: getattr(self, current) - getattr(other, current)})

        return data

    def __str__(self):
        return '{} | {}: {} Watt'.format(
            self.__class__.__name__, self.read_at, self.currently_delivered * 1000
        )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Electricity consumption')
        verbose_name_plural = verbose_name


class GasConsumption(models.Model):
    """ Interpolated gas reading, containing the actual usage, based on the reading before (if any). """
    read_at = models.DateTimeField(unique=True)
    delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Last meter position read")
    )
    # This value is not provided by DSMR so we calculate the difference relative to the previous reading.
    currently_delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Delivered value, based on the previous reading")
    )

    def __str__(self):
        return '{} | {}: {} m3'.format(
            self.__class__.__name__, self.read_at, self.currently_delivered
        )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Gas consumption')
        verbose_name_plural = verbose_name
