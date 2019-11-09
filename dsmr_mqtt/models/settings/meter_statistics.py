from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class SplitTopicMeterStatisticsMQTTSettings(ModelUpdateMixin, SingletonModel):
    """ MQTT splitted meter statistics per field, mapped to topics. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether meter statistics are sent to the broker, having each field sent to a different topic.')
    )
    formatting = models.TextField(
        default='''
[mapping]
# DATA = TOPIC PATH
dsmr_version = dsmr/meter-stats/dsmr_version
electricity_tariff = dsmr/meter-stats/electricity_tariff
power_failure_count = dsmr/meter-stats/power_failure_count
long_power_failure_count = dsmr/meter-stats/long_power_failure_count
voltage_sag_count_l1 = dsmr/meter-stats/voltage_sag_count_l1
voltage_sag_count_l2 = dsmr/meter-stats/voltage_sag_count_l2
voltage_sag_count_l3 = dsmr/meter-stats/voltage_sag_count_l3
voltage_swell_count_l1 = dsmr/meter-stats/voltage_swell_count_l1
voltage_swell_count_l2 = dsmr/meter-stats/voltage_swell_count_l2
voltage_swell_count_l3 = dsmr/meter-stats/voltage_swell_count_l3
rejected_telegrams = dsmr/meter-stats/rejected_telegrams
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names to separate topics sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('(Data source) Meter Statistics: Split topic')
