from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext as _


class DsmrReading(models.Model):
    """ DSMR P1 telegram reading. Contains most of the raw data read from serial port. """
    DSMR_MAPPING = {
        "0-0:1.0.0": "timestamp",
        "1-0:1.8.1": "electricity_delivered_1",
        "1-0:2.8.1": "electricity_returned_1",
        "1-0:1.8.2": "electricity_delivered_2",
        "1-0:2.8.2": "electricity_returned_2",
        "0-0:96.14.0": "electricity_tariff",
        "1-0:1.7.0": "electricity_currently_delivered",
        "1-0:2.7.0": "electricity_currently_returned",
        "0-0:96.7.21": "power_failure_count",
        "0-0:96.7.9": "long_power_failure_count",
        "1-0:32.32.0": "voltage_sag_count_l1",
        "1-0:52.32.0": "voltage_sag_count_l2",
        "1-0:72.32.0": "voltage_sag_count_l3",
        "1-0:32.36.0": "voltage_swell_count_l1",
        "1-0:52.36.0": "voltage_swell_count_l2",
        "1-0:72.36.0": "voltage_swell_count_l3",
        "0-1:24.2.1": ("extra_device_timestamp", "extra_device_delivered"),
    }

    class Meta:
        ordering = ['timestamp']

    timestamp = models.DateTimeField()
    electricity_delivered_1 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter Reading electricity delivered to client (low tariff) in 0,001 kWh")
    )
    electricity_returned_1 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter Reading electricity delivered by client (low tariff) in 0,001 kWh")
    )
    electricity_delivered_2 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh")
    )
    electricity_returned_2 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh")
    )
    electricity_tariff = models.IntegerField(
        help_text=_(
            "Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g "
            "boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff "
            "code 2 is used for normal tariff."
        )
    )
    electricity_currently_delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Actual electricity power delivered (+P) in 1 Watt resolution")
    )
    electricity_currently_returned = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Actual electricity power received (-P) in 1 Watt resolution")
    )
    power_failure_count = models.IntegerField(
        help_text=_("Number of power failures in any phases")
    )
    long_power_failure_count = models.IntegerField(
        help_text=_("Number of long power failures in any phase")
    )
    voltage_sag_count_l1 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L1")
    )
    voltage_sag_count_l2 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L2 (polyphase meters only)")
    )
    voltage_sag_count_l3 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L3 (polyphase meters only)")
    )
    voltage_swell_count_l1 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L1")
    )
    voltage_swell_count_l2 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L2 (polyphase meters only)")
    )
    voltage_swell_count_l3 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L3 (polyphase meters only)")
    )
    extra_device_timestamp = models.DateTimeField(
        help_text=_("Last hourly reading timestamp")
    )
    extra_device_delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Last hourly value delivered to client")
    )
    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Whether this reading has been processed for individual splitting")
    )

    def __str__(self):
        return '#{} | {}: {} kWh'.format(
            self.id, self.timestamp, self.electricity_currently_delivered
        )


class ElectricityStatistics(models.Model):
    """ Daily electricity statistics for data not subject to changing hourly. """
    day = models.DateField(unique=True)
    power_failure_count = models.IntegerField(
        help_text=_("Number of power failures in any phases")
    )
    long_power_failure_count = models.IntegerField(
        help_text=_("Number of long power failures in any phase")
    )
    voltage_sag_count_l1 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L1")
    )
    voltage_sag_count_l2 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L2 (polyphase meters only)")
    )
    voltage_sag_count_l3 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L3 (polyphase meters only)")
    )
    voltage_swell_count_l1 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L1")
    )
    voltage_swell_count_l2 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L2 (polyphase meters only)")
    )
    voltage_swell_count_l3 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L3 (polyphase meters only)")
    )

    def is_equal(self, other):
        for field in self._meta.fields:
            if field.name != 'id' and getattr(self, field.name) != getattr(other, field.name):
                return False

        return True


class ElectricityConsumption(models.Model):
    """ Point in time of electricity consumption, extracted from reading. """
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


class GasConsumption(models.Model):
    """ Hourly consumption, based on the previous value one hour ago. """
    read_at = models.DateTimeField(unique=True)
    delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Last hourly value delivered to client")
    )
    currently_delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Actual value delivered to client, since the last hour")
    )

    def __str__(self):
        return '{} | {}: {} m3'.format(
            self.__class__.__name__, self.read_at, self.currently_delivered
        )


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
    electricity_1_price = models.DecimalField(max_digits=11, decimal_places=5)
    electricity_2_price = models.DecimalField(max_digits=11, decimal_places=5)
    gas_price = models.DecimalField(max_digits=11, decimal_places=5)
