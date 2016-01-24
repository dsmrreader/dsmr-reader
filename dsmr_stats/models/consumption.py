from django.db import models
from django.utils.translation import ugettext as _


class ElectricityConsumption(models.Model):
    """ Point in time of electricity consumption, extracted from reading(s). """
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
    tariff = models.IntegerField(
        help_text=_(
            "Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g "
            "boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff "
            "code 2 is used for normal tariff."
        )
    )
    currently_delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Actual electricity power delivered (+P) in 1 Watt resolution")
    )
    currently_returned = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Actual electricity power received (-P) in 1 Watt resolution")
    )

    def __str__(self):
        return '{} | {}: {} Watt'.format(
            self.__class__.__name__, self.read_at, self.currently_delivered * 1000
        )

    class Meta:
        default_permissions = tuple()


class GasConsumption(models.Model):
    """ Hourly consumption, interpolated on the previous value read the hour before. """
    read_at = models.DateTimeField(unique=True)
    delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Last hourly value delivered to client")
    )
    # This value is not provided by DSMR so we calculate the difference from the previous reading.
    currently_delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Actual value delivered to client, since the last hour")
    )

    def __str__(self):
        return '{} | {}: {} m3'.format(
            self.__class__.__name__, self.read_at, self.currently_delivered
        )

    class Meta:
        default_permissions = tuple()
