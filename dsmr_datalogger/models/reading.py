from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class DsmrReadingManager(models.Manager):
    def unprocessed(self):
        return self.get_queryset().filter(processed=False)

    def processed(self):
        return self.get_queryset().filter(processed=True)


class DsmrReading(models.Model):
    """
    Core data read from a P1 DSMR telegram (meter reading).
    """
    objects = DsmrReadingManager()

    timestamp = models.DateTimeField(
        help_text=_("Timestamp indicating when the reading was taken, according to the meter")
    )
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
    extra_device_timestamp = models.DateTimeField(
        null=True,
        default=None,
        help_text=_("Last hourly reading timestamp")
    )
    extra_device_delivered = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Last hourly value delivered to client")
    )
    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Whether this reading has been processed for merging into statistics")
    )

    class Meta:
        default_permissions = tuple()
        ordering = ['timestamp']
        verbose_name = _('DSMR reading')

    def __str__(self):
        return '{}: {} kWh'.format(
            self.id, self.timestamp, self.electricity_currently_delivered
        )


class MeterStatistics(SingletonModel):
    """ Meter statistics, but only exists as a single record, containing the latest data. """
    timestamp = models.DateTimeField(
        help_text=_("Timestamp indicating when the reading was taken, according to the meter"),
        auto_now=True
    )
    electricity_tariff = models.IntegerField(
        help_text=_(
            "Tariff indicator electricity. The tariff indicator can be used to switch tariff  "
            "dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff "
            "code 1 is used for low tariff and tariff code 2 is used for normal tariff."
        ),
        null=True,
        default=None
    )
    power_failure_count = models.IntegerField(
        help_text=_("Number of power failures in any phases"),
        null=True,
        default=None
    )
    long_power_failure_count = models.IntegerField(
        help_text=_("Number of long power failures in any phase"),
        null=True,
        default=None
    )
    voltage_sag_count_l1 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L1"),
        null=True,
        default=None
    )
    voltage_sag_count_l2 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L2 (polyphase meters only)"),
        null=True,
        default=None
    )
    voltage_sag_count_l3 = models.IntegerField(
        help_text=_("Number of voltage sags/dips in phase L3 (polyphase meters only)"),
        null=True,
        default=None
    )
    voltage_swell_count_l1 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L1"),
        null=True,
        default=None
    )
    voltage_swell_count_l2 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L2 (polyphase meters only)"),
        null=True,
        default=None
    )
    voltage_swell_count_l3 = models.IntegerField(
        help_text=_("Number of voltage swells in phase L3 (polyphase meters only)"),
        null=True,
        default=None
    )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('DSMR Meter statistics')

    def __str__(self):
        return '{} @ {}'.format(self.__class__.__name__, self.timestamp)
