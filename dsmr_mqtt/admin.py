from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_mqtt.models.settings import broker, day_totals, telegram, meter_statistics
from dsmr_backend.mixins import ReadOnlyAdminModel
from dsmr_mqtt.models import queue


@admin.register(broker.MQTTBrokerSettings)
class MQTTBrokerSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['hostname', 'port', 'secure', 'client_id'],
                'description': _(
                    'Detailed instructions for configuring MQTT can be found here: '
                    '<a href="https://dsmr-reader.readthedocs.io/nl/v2/mqtt.html">Documentation</a>'
                )
            }
        ),
        (
            _('Advanced'), {
                'fields': ['username', 'password', 'qos'],
                'description': _(
                    'These broker settings apply to all enabled MQTT configurations.'
                )
            }
        ),
    )


@admin.register(telegram.RawTelegramMQTTSettings)
class RawTelegramMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'topic'],
                'description': _(
                    'Triggered by the datalogger or any API calls using the v1 API. '
                    'Allows you to pass on any incoming raw telegrams to the MQTT broker.'
                )
            }
        ),
    )


@admin.register(telegram.JSONTelegramMQTTSettings)
class JSONTelegramMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'topic', 'formatting', 'use_local_timezone'],
                'description': _(
                    'Triggered by any method of reading insertion (datalogger or API). '
                    'Allows you to send newly created readings to the MQTT broker, as a JSON message. You can alter '
                    'the field names used in the JSON message. Removing lines will remove fields from the message as '
                    'well. '
                    '''Default value:
<pre>
[mapping]
id = id
timestamp = timestamp
electricity_delivered_1 = electricity_delivered_1
electricity_returned_1 = electricity_returned_1
electricity_delivered_2 = electricity_delivered_2
electricity_returned_2 = electricity_returned_2
electricity_currently_delivered = electricity_currently_delivered
electricity_currently_returned = electricity_currently_returned
phase_currently_delivered_l1 = phase_currently_delivered_l1
phase_currently_delivered_l2 = phase_currently_delivered_l2
phase_currently_delivered_l3 = phase_currently_delivered_l3
phase_currently_returned_l1 = phase_currently_returned_l1
phase_currently_returned_l2 = phase_currently_returned_l2
phase_currently_returned_l3 = phase_currently_returned_l3
extra_device_timestamp = extra_device_timestamp
extra_device_delivered = extra_device_delivered
phase_voltage_l1 = phase_voltage_l1
phase_voltage_l2 = phase_voltage_l2
phase_voltage_l3 = phase_voltage_l3
</pre>
'''
                )
            }
        ),
    )


@admin.register(telegram.SplitTopicTelegramMQTTSettings)
class SplitTopicTelegramMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'formatting', 'use_local_timezone'],
                'description': _(
                    'Triggered by any method of reading insertion (datalogger or API). '
                    'Allows you to send newly created readings to the MQTT broker, splitted per field. You can '
                    'designate each field name to a different topic. Removing lines will prevent those fields from '
                    'being broadcast as well. '
                    '''Default value:
<pre>
[mapping]
id = dsmr/reading/id
timestamp = dsmr/reading/timestamp
electricity_delivered_1 = dsmr/reading/electricity_delivered_1
electricity_returned_1 = dsmr/reading/electricity_returned_1
electricity_delivered_2 = dsmr/reading/electricity_delivered_2
electricity_returned_2 = dsmr/reading/electricity_returned_2
electricity_currently_delivered = dsmr/reading/electricity_currently_delivered
electricity_currently_returned = dsmr/reading/electricity_currently_returned
phase_currently_delivered_l1 = dsmr/reading/phase_currently_delivered_l1
phase_currently_delivered_l2 = dsmr/reading/phase_currently_delivered_l2
phase_currently_delivered_l3 = dsmr/reading/phase_currently_delivered_l3
phase_currently_returned_l1 = dsmr/reading/phase_currently_returned_l1
phase_currently_returned_l2 = dsmr/reading/phase_currently_returned_l2
phase_currently_returned_l3 = dsmr/reading/phase_currently_returned_l3
extra_device_timestamp = dsmr/reading/extra_device_timestamp
extra_device_delivered = dsmr/reading/extra_device_delivered
phase_voltage_l1 = dsmr/reading/phase_voltage_l1
phase_voltage_l2 = dsmr/reading/phase_voltage_l2
phase_voltage_l3 = dsmr/reading/phase_voltage_l3
</pre>
'''
                )
            }
        ),
    )


@admin.register(day_totals.JSONDayTotalsMQTTSettings)
class JSONDayTotalsMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'topic', 'formatting'],
                'description': _(
                    'Triggered by any method of reading insertion (datalogger or API). '
                    'Send the current day totals to the broker. You can alter the the field names used in the JSON '
                    'message. Removing lines will remove fields from the message as well. '
                    '''Default value:
<pre>
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
</pre>
'''
                )
            }
        ),
    )


@admin.register(day_totals.SplitTopicDayTotalsMQTTSettings)
class SplitTopicDayTotalsMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'formatting'],
                'description': _(
                    'Triggered by any method of reading insertion (datalogger or API). '
                    'Allows you to send day totals (dashboard) to the MQTT broker, splitted per field. You can '
                    'designate each field name to a different topic. Removing lines will prevent those fields from '
                    'being broadcast as well. '
                    '''Default value:
<pre>
[mapping]
# DATA = JSON FIELD
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
</pre>
'''
                )
            }
        ),
    )


@admin.register(meter_statistics.SplitTopicMeterStatisticsMQTTSettings)
class SplitTopicMeterStatisticsMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'formatting'],
                'description': _(
                    'Triggered by any method of reading insertion (datalogger or API). '
                    'Allows you to send meter statistics to the MQTT broker, splitted per field. You can '
                    'designate each field name to a different topic. Removing lines will prevent those fields from '
                    'being broadcast as well. '
                    '''Default value:
<pre>
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
</pre>
'''
                )
            }
        ),
    )


@admin.register(queue.Message)
class MessageAdmin(ReadOnlyAdminModel):
    list_display = ('topic', 'payload')
