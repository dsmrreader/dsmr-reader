from django.db import models
from django.utils.translation import ugettext as _


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
        """
        Checks whether another statistics object equals this one. It actually is just a lousy way of
        preventing unneeded database writes.

        We could also override the eq() operator, but we rather use any builtins provided by Django.
        """
        for field in self._meta.fields:
            if field.name != 'id' and getattr(self, field.name) != getattr(other, field.name):
                return False

        return True

    class Meta:
        default_permissions = tuple()
