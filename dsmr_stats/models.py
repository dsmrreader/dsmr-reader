from django.db import models
from django.utils.translation import ugettext as _


class DsmrReading(models.Model):
    version = models.DateTimeField(verbose_name="1-3:0.2.8")
    timestamp = models.BigIntegerField(verbose_name="0-0:1.0.0")
    electricity_delivered_1 = models.IntegerField(
        verbose_name="1-0:1.8.1",
        help_text=_("Meter Reading electricity delivered to client (low tariff) in 0,001 kWh")
    )
    electricity_returned_1 = models.IntegerField(
        verbose_name="1-0:2.8.1",
        help_text=_("Meter Reading electricity delivered by client (low tariff) in 0,001 kWh")
    )
    electricity_delivered_2 = models.IntegerField(
        verbose_name="1-0:1.8.2",
        help_text=_("Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh")
    )
    electricity_returned_2 = models.IntegerField(
        verbose_name="1-0:2.8.2",
        help_text=_("Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh")
    )
    electricity_tariff = models.IntegerField(
        verbose_name="0-0:96.14.0",
        help_text=_(
            "Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g "
            "boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff "
            "code 2 is used for normal tariff."
        )
    )
    electricity_currently_delivered = models.IntegerField(
        verbose_name="1-0:1.7.0",
        help_text=_("Actual electricity power delivered (+P) in 1 Watt resolution")
    )
    electricity_currently_returned = models.IntegerField(
        verbose_name="1-0:2.7.0",
        help_text=_("Actual electricity power received (-P) in 1 Watt resolution")
    )
    power_failure_count = models.IntegerField(
        verbose_name="0-0:96.7.21",
        help_text=_("Number of power failures in any phases")
    )
    long_power_failure_count = models.IntegerField(
        verbose_name="0-0:96.7.9",
        help_text=_("Number of long power failures in any phase")
    )
    voltage_sag_count_l1 = models.IntegerField(
        verbose_name="1-0:32.32.0",
        help_text=_("Number of voltage sags/dips in phase L1")
    )
    voltage_sag_count_l2 = models.IntegerField(
        verbose_name="1-0:52.32.0",
        help_text=_("Number of voltage sags/dips in phase L2 (polyphase meters only)")
    )
    voltage_sag_count_l3 = models.IntegerField(
        verbose_name="1-0:72.32.0",
        help_text=_("Number of voltage sags/dips in phase L3 (polyphase meters only)")
    )
    voltage_swell_count_l1 = models.IntegerField(
        verbose_name="1-0:32.36.0",
        help_text=_("Number of voltage swells in phase L1")
    )
    voltage_swell_count_l2 = models.IntegerField(
        verbose_name="1-0:52.36.0",
        help_text=_("Number of voltage swells in phase L2 (polyphase meters only)")
    )
    voltage_swell_count_l3 = models.IntegerField(
        verbose_name="1-0:72.36.0",
        help_text=_("Number of voltage swells in phase L3 (polyphase meters only)")
    )
    extra_device_timestamp = models.IntegerField(
        verbose_name="0-1:24.2.1",
        help_text=_("Last hourly reading timestamp")
    )
    extra_device_delivered = models.IntegerField(
        verbose_name="0-1:24.2.1",
        help_text=_("Last hourly value delivered to client")
    )
    extra_device_valve_position = models.IntegerField(
        verbose_name="0-1:24.4.0",
        help_text=_("Valve position (on/off/released)")
    )
