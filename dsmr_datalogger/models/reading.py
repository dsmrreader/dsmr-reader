from django.db import models
from django.utils.translation import ugettext_lazy as _


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
    phase_currently_delivered_l1 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Instantaneous active power L1 (+P) in W resolution")
    )
    phase_currently_delivered_l2 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Instantaneous active power L2 (+P) in W resolution")
    )
    phase_currently_delivered_l3 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Instantaneous active power L3 (+P) in W resolution")
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
        verbose_name = _('DSMR reading (read only)')
        verbose_name_plural = _('DSMR readings (read only)')

    def __str__(self):
        return '{}: {} kWh'.format(self.id, self.timestamp, self.electricity_currently_delivered)
