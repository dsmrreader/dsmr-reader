from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class MeterStatistics(SingletonModel):
    """ Meter statistics, but only exists as a single record, containing the latest data. """
    timestamp = models.DateTimeField(
        help_text=_("Timestamp indicating when the reading was taken"),
        auto_now=True
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
    rejected_telegrams = models.IntegerField(
        help_text=_("Number of rejected telegrams due to invalid CRC checksum"),
        default=0
    )
    latest_telegram = models.TextField(
        help_text=_("The latest telegram succesfully read. Please note that only the last telegram is saved"),
        null=True,
        default=None
    )

    class Meta:
        default_permissions = tuple()
        verbose_name = _('DSMR Meter statistics (read only)')
        verbose_name_plural = verbose_name

    def __str__(self):
        return '{} @ {}'.format(self.__class__.__name__, self.timestamp)
