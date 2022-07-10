from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.utils import timezone

from dsmr_backend.mixins import ModelUpdateMixin


class DsmrReadingManager(models.Manager):
    def unprocessed(self):
        return self.get_queryset().filter(processed=False)

    def processed(self):
        return self.get_queryset().filter(processed=True)


class DsmrReading(ModelUpdateMixin, models.Model):
    """
    Core data read from a P1 DSMR telegram (meter reading).
    """
    objects = DsmrReadingManager()

    processed = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Whether this reading has been processed for merging into statistics")
    )
    timestamp = models.DateTimeField(
        db_index=True,
        help_text=_("Timestamp indicating when the reading was taken, according to the smart meter")
    )
    electricity_delivered_1 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter position stating electricity delivered (Dutch users: low tariff) in kWh")
    )
    electricity_returned_1 = models.DecimalField(
        max_digits=9,
        decimal_places=3,
        help_text=_("Meter position stating electricity returned (Dutch users: low tariff) in kWh")
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
    phase_currently_returned_l1 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Current electricity returned by phase L1 (in kW)")
    )
    phase_currently_returned_l2 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Current electricity returned by phase L2 (in kW)")
    )
    phase_currently_returned_l3 = models.DecimalField(
        null=True,
        default=None,
        max_digits=9,
        decimal_places=3,
        help_text=_("Current electricity returned by phase L3 (in kW)")
    )
    phase_voltage_l1 = models.DecimalField(
        null=True,
        default=None,
        max_digits=4,
        decimal_places=1,
        help_text=_("Current voltage for phase L1 (in V)")
    )
    phase_voltage_l2 = models.DecimalField(
        null=True,
        default=None,
        max_digits=4,
        decimal_places=1,
        help_text=_("Current voltage for phase L2 (in V)")
    )
    phase_voltage_l3 = models.DecimalField(
        null=True,
        default=None,
        max_digits=4,
        decimal_places=1,
        help_text=_("Current voltage for phase L3 (in V)")
    )
    phase_power_current_l1 = models.IntegerField(
        null=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(999)],
        help_text=_("Power/current for phase L1 (in A)")
    )
    phase_power_current_l2 = models.IntegerField(
        null=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(999)],
        help_text=_("Power/current for phase L2 (in A)")
    )
    phase_power_current_l3 = models.IntegerField(
        null=True,
        default=None,
        validators=[MinValueValidator(0), MaxValueValidator(999)],
        help_text=_("Power/current for phase L3 (in A)")
    )

    class Meta:
        default_permissions = tuple()
        ordering = ['timestamp']
        verbose_name = _('DSMR reading')
        verbose_name_plural = _('DSMR readings')

    def convert_to_local_timezone(self):
        """ Converts the timestamp to the local time zone used. Only affects this instance, does not update record! """
        self.timestamp = timezone.localtime(self.timestamp)

        if self.extra_device_timestamp:
            self.extra_device_timestamp = timezone.localtime(self.extra_device_timestamp)

    def __str__(self):
        return '{} @ {}'.format(
            self.id, timezone.localtime(self.timestamp)
        )
