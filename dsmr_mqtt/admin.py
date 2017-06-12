from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_mqtt.models.settings import MQTTBrokerSettings, RawTelegramMQTTSettings, JSONTelegramMQTTSettings,\
    SplitTopicTelegramMQTTSettings


@admin.register(MQTTBrokerSettings)
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


@admin.register(RawTelegramMQTTSettings)
class RawTelegramMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'topic'],
                'description': _(
                    'Allows you to pass on any incoming raw telegrams to the MQTT broker. Triggered by the datalogger '
                    'or any API calls using the v1 API.'
                )
            }
        ),
    )


@admin.register(JSONTelegramMQTTSettings)
class JSONTelegramMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'topic', 'formatting'],
                'description': _(
                    'Allows you to send newly created readings to the MQTT broker, as a JSON message. You can alter '
                    'the field names used in the JSON message. Triggered by any method of reading insertion '
                    '(datalogger or API).'
                )
            }
        ),
    )


@admin.register(SplitTopicTelegramMQTTSettings)
class SplitTopicTelegramMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'formatting'],
                'description': _(
                    'Allows you to send newly created readings to the MQTT broker, splitted per field. You can '
                    'designate each field name to a different topic. Triggered by any method of reading insertion '
                    '(datalogger or API).'
                )
            }
        ),
    )
