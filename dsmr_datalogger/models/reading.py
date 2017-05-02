from django.utils.translation import ugettext_lazy as _
from django.db import models
from django.utils import timezone


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
        db_index=True,
        help_text=_("Timestamp indicating when the reading was taken, according to the smart meter")
    )
    electricity_delivered_1 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter position stating electricity delivered (low tariff) in kWh")
    )
    electricity_returned_1 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter position stating electricity returned (low tariff) in kWh")
    )
    electricity_delivered_2 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter position stating electricity delivered (normal tariff) in kWh")
    )
    electricity_returned_2 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter position stating electricity returned (normal tariff) in kWh")
    )
    electricity_currently_delivered = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Current electricity delivered in kW")
    )
    electricity_currently_returned = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Current electricity returned in kW")
    )
    phase_currently_delivered_l1 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Current electricity used by phase L1 (in kW)")
    )
    phase_currently_delivered_l2 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Current electricity used by phase L2 (in kW)")
    )
    phase_currently_delivered_l3 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Current electricity used by phase L3 (in kW)")
    )
    extra_device_timestamp = models.DateTimeField(
        null=True,
        default=None,
        help_text=_("Last timestamp read from the extra device connected (gas meter)")
    )
    extra_device_delivered = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Last value read from the extra device connected (gas meter)")
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
        return '{} @ {} ({} kW)'.format(
            self.id, timezone.localtime(self.timestamp), self.electricity_currently_delivered
        )
