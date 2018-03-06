from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class JSONDayTotalsMQTTSettings(SingletonModel):
    """ MQTT JSON Dashboard overview. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether the day totals are sent to the broker, in JSON format.')
    )
    topic = models.CharField(
        max_length=256,
        default='dsmr/day-totals',
        verbose_name=_('Topic path'),
        help_text=_('The topic to send the JSON formatted message to.')
    )
    formatting = models.TextField(
        default='''
[mapping]
# DATA = JSON FIELD
electricity1 = electricity1
electricity2 = electricity2
electricity1_returned = electricity1_returned
electricity2_returned = electricity2_returned
electricity_merged = electricity_merged
electricity_returned_merged = electricity_returned_merged
electricity1_cost = electricity1_cost
electricity2_cost = electricity2_cost
electricity_cost_merged = electricity_cost_merged

# Gas (if any)
gas = gas
gas_cost = gas_cost
total_cost = total_cost

# Your energy supplier prices (if set)
energy_supplier_price_electricity_delivered_1 = energy_supplier_price_electricity_delivered_1
energy_supplier_price_electricity_delivered_2 = energy_supplier_price_electricity_delivered_2
energy_supplier_price_electricity_returned_1 = energy_supplier_price_electricity_returned_1
energy_supplier_price_electricity_returned_2 = energy_supplier_price_electricity_returned_2
energy_supplier_price_gas = energy_supplier_price_gas
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names used in the JSON message sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('MQTT JSON day totals configuration')
