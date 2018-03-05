from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_mqtt.models import settings


@admin.register(settings.MQTTBrokerSettings)
class MQTTBrokerSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['hostname', 'port', 'username', 'password', 'client_id'],
                'description': _(
                    'These broker settings apply to all enabled MQTT configurations.'
                )
            }
        ),
    )


@admin.register(settings.RawTelegramMQTTSettings)
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


@admin.register(settings.JSONTelegramMQTTSettings)
class JSONTelegramMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'topic', 'formatting'],
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
extra_device_timestamp = extra_device_timestamp
extra_device_delivered = extra_device_delivered
</pre>
'''
                )
            }
        ),
    )


@admin.register(settings.SplitTopicTelegramMQTTSettings)
class SplitTopicTelegramMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'formatting'],
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
extra_device_timestamp = dsmr/reading/extra_device_timestamp
extra_device_delivered = dsmr/reading/extra_device_delivered
</pre>
'''
                )
            }
        ),
    )


@admin.register(settings.JSONDayTotalsMQTTSettings)
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
gas = gas
gas_cost = gas_cost
total_cost = total_cost
</pre>
'''
                )
            }
        ),
    )
