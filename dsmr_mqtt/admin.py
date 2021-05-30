from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin

from dsmr_mqtt.models.settings import broker, day_totals, telegram, meter_statistics, consumption, period_totals
from dsmr_backend.mixins import DeletionOnlyAdminModel
from dsmr_mqtt.models import queue


@admin.register(broker.MQTTBrokerSettings)
class MQTTBrokerSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'hostname', 'port', 'secure', 'client_id'],
                'description': _(
                    'The backend process should automatically restart to apply changes.'
                )
            }
        ),
        (
            _('Misc'), {
                'fields': ['username', 'password'],
            }
        )
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
                    {}
                    </pre>
                    '''.format(
                        [
                            x.default for x in telegram.JSONTelegramMQTTSettings._meta.get_fields()
                            if x.name == 'formatting'
                        ][0]
                    )
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
                    {}
                    </pre>
                    '''.format(
                        [
                            x.default for x in telegram.SplitTopicTelegramMQTTSettings._meta.get_fields()
                            if x.name == 'formatting'
                        ][0]
                    )
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
                    {}
                    </pre>
                    '''.format(
                        [
                            x.default for x in day_totals.JSONDayTotalsMQTTSettings._meta.get_fields()
                            if x.name == 'formatting'
                        ][0]
                    )
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
                    {}
                    </pre>
                    '''.format(
                        [
                            x.default for x in day_totals.SplitTopicDayTotalsMQTTSettings._meta.get_fields()
                            if x.name == 'formatting'
                        ][0]
                    )
                )
            }
        ),
    )


@admin.register(period_totals.JSONCurrentPeriodTotalsMQTTSettings)
class JSONPeriodTotalsUpdateMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'topic', 'formatting'],
                'description': _(
                    'Contains the totals for the current month and current year. '
                    'Payload is a customizable JSON structure. '
                    '''Default value:
                    <pre>
                    {}
                    </pre>
                    '''.format(
                        [
                            x.default for x in period_totals.JSONCurrentPeriodTotalsMQTTSettings._meta.get_fields()
                            if x.name == 'formatting'
                        ][0]
                    )
                )
            }
        ),
    )


@admin.register(period_totals.SplitTopicCurrentPeriodTotalsMQTTSettings)
class SplitTopicPeriodTotalsUpdateMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'formatting'],
                'description': _(
                    'Contains the totals for the current month and current year. '
                    'Payload is sent on a per field per topic basis. '
                    '''Default value:
                    <pre>
                    {}
                    </pre>
                    '''.format([
                        x.default for x in period_totals.SplitTopicCurrentPeriodTotalsMQTTSettings._meta.get_fields()
                        if x.name == 'formatting'
                    ][0])
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
                    {}
                    </pre>
                    '''.format(
                        [
                            x.default for x in meter_statistics.SplitTopicMeterStatisticsMQTTSettings._meta.get_fields()
                            if x.name == 'formatting'
                        ][0]
                    )
                )
            }
        ),
    )


@admin.register(consumption.JSONGasConsumptionMQTTSettings)
class JSONGasConsumptionMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'topic', 'formatting'],
                'description': _(
                    'Triggered when a different gas reading is processed. '
                    'Allows you to send gas consumption to the MQTT broker, as a JSON message. You can alter '
                    'the field names used in the JSON message. Removing lines will remove fields from the message as '
                    'well. '
                    '''Default value:
                    <pre>
                    {}
                    </pre>
                    '''.format(
                        [
                            x.default for x in consumption.JSONGasConsumptionMQTTSettings._meta.get_fields()
                            if x.name == 'formatting'
                        ][0]
                    )
                )
            }
        ),
    )


@admin.register(consumption.SplitTopicGasConsumptionMQTTSettings)
class SplitTopicGasConsumptionMQTTSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['enabled', 'formatting'],
                'description': _(
                    'Triggered when a different gas reading is processed. '
                    'Allows you to send gas consumption to the MQTT broker, splitted per field. You can '
                    'designate each field name to a different topic. Removing lines will prevent those fields from '
                    'being broadcast as well. '
                    '''Default value:
                    <pre>
                    {}
                    </pre>
                    '''.format(
                        [
                            x.default for x in consumption.SplitTopicGasConsumptionMQTTSettings._meta.get_fields()
                            if x.name == 'formatting'
                        ][0]
                    )
                )
            }
        ),
    )


@admin.register(queue.Message)
class MessageAdmin(DeletionOnlyAdminModel):
    list_display = ('topic', 'payload')
