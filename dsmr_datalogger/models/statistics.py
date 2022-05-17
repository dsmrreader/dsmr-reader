from django.db import models
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel
import django.db.models.signals

from dsmr_backend.mixins import ModelUpdateMixin


class MeterStatistics(ModelUpdateMixin, SingletonModel):
    """ Meter statistics, but only exists as a single record, containing the latest data. """

    timestamp = models.DateTimeField(
        help_text=_("Timestamp indicating when the reading was taken"),
        default=timezone.now
    )
    dsmr_version = models.CharField(
        help_text=_("DSMR version"),
        max_length=2,
        null=True,
        default=None
    )
    electricity_tariff = models.IntegerField(
        help_text=_(
            "Tariff indicator electricity. The tariff indicator can be used to switch tariff  "
            "dependent loads e.g boilers. This is responsibility of the P1 user."
        ),
        null=True,
        default=None
    )
    power_failure_count = models.IntegerField(
        help_text=_("Number of power failures in any phase"),
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
    rejected_telegrams = models.IntegerField(
        help_text=_("Number of rejected telegrams due to invalid CRC checksum"),
        default=0
    )
    latest_telegram = models.TextField(
        help_text=_(
            "The latest telegram succesfully read. Please note that only the latest telegram is saved here and will be "
            "overwritten each time."
        ),
        null=True,
        default=None
    )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('DSMR Meter statistics (read only)')
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{} @ {}'.format(self.__class__.__name__, self.timestamp)


class MeterStatisticsChange(models.Model):
    created_at = models.DateTimeField(
        verbose_name=_("Created at"),
        help_text=_("Timestamp indicating when the change was logged"),
        auto_now_add=True
    )
    field = models.CharField(
        verbose_name=_("Field"),
        help_text=_("The name of the statistics field that changed"),
        max_length=64
    )
    old_value = models.CharField(
        verbose_name=_("Old value"),
        max_length=32
    )
    new_value = models.CharField(
        verbose_name=_("New value"),
        max_length=32
    )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('DSMR Meter statistics change')
        verbose_name_plural = _('DSMR Meter statistics changes')

    def __str__(self):
        return '{} @ {}'.format(self.__class__.__name__, self.created_at)


@receiver(django.db.models.signals.pre_save, sender=MeterStatistics)
def _on_meter_statistics_pre_save_signal(instance, raw, update_fields, **kwargs):
    """ Logs any changes. """
    if raw or not update_fields:
        return

    WATCHED_FIELDS = [
        x.name for x in MeterStatistics._meta.get_fields() if x.name not in (
            # Excluded fields listed here:
            'id', 'timestamp', 'dsmr_version', 'electricity_tariff', 'rejected_telegrams', 'latest_telegram'
        )
    ]

    old_instance = MeterStatistics.get_solo()

    for current_field in update_fields:
        if current_field not in WATCHED_FIELDS:
            continue

        old_value = getattr(old_instance, current_field)
        new_value = getattr(instance, current_field)

        # Only log changes and do not log the initial statistics read directly after install.
        if new_value == old_value or old_value is None:
            continue

        MeterStatisticsChange.objects.create(
            field=current_field,
            old_value=str(old_value),
            new_value=str(new_value),
        )
