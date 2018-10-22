from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class JSONDayTotalsMQTTSettings(SingletonModel):
    """ MQTT JSON Dashboard overview. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether the day consumption is sent to the broker, in JSON format.')
    )
    topic = models.CharField(
        max_length=256,
        default='dsmr/day-consumption',
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
        verbose_name = _('MQTT: Day consumption (as JSON) configuration')


class SplitTopicDayTotalsMQTTSettings(SingletonModel):
    """ MQTT splitted day totals per field, mapped to topics. """
    enabled = models.BooleanField(
        default=False,
        verbose_name=_('Enabled'),
        help_text=_('Whether day consumption is sent to the broker, having each field sent to a different topic.')
    )
    formatting = models.TextField(
        default='''
[mapping]
# DATA = TOPIC PATH
electricity1 = dsmr/day-consumption/electricity1
electricity2 = dsmr/day-consumption/electricity2
electricity1_returned = dsmr/day-consumption/electricity1_returned
electricity2_returned = dsmr/day-consumption/electricity2_returned
electricity_merged = dsmr/day-consumption/electricity_merged
electricity_returned_merged = dsmr/day-consumption/electricity_returned_merged
electricity1_cost = dsmr/day-consumption/electricity1_cost
electricity2_cost = dsmr/day-consumption/electricity2_cost
electricity_cost_merged = dsmr/day-consumption/electricity_cost_merged

# Gas (if any)
gas = dsmr/day-consumption/gas
gas_cost = dsmr/day-consumption/gas_cost
total_cost = dsmr/day-consumption/total_cost

# Your energy supplier prices (if set)
energy_supplier_price_electricity_delivered_1 = dsmr/day-consumption/energy_supplier_price_electricity_delivered_1
energy_supplier_price_electricity_delivered_2 = dsmr/day-consumption/energy_supplier_price_electricity_delivered_2
energy_supplier_price_electricity_returned_1 = dsmr/day-consumption/energy_supplier_price_electricity_returned_1
energy_supplier_price_electricity_returned_2 = dsmr/day-consumption/energy_supplier_price_electricity_returned_2
energy_supplier_price_gas = dsmr/day-consumption/energy_supplier_price_gas
''',
        verbose_name=_('Formatting'),
        help_text=_('Maps the field names to separate topics sent to the broker.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('MQTT: Day consumption (per split topic) configuration')
