import configparser
import json
from typing import NoReturn, Dict

from django.core import serializers
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_mqtt.models.settings import day_totals, telegram, meter_statistics, consumption, period_totals
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.statistics import MeterStatistics
import dsmr_consumption.services
import dsmr_mqtt.services.messages
import dsmr_stats.services


def publish_raw_dsmr_telegram(data: str) -> NoReturn:
    """ Publishes a raw DSMR telegram string to a broker, if set and enabled. """
    raw_settings = telegram.RawTelegramMQTTSettings.get_solo()

    if not raw_settings.enabled:
        return

    dsmr_mqtt.services.messages.queue_message(topic=raw_settings.topic, payload=data)


def publish_json_dsmr_reading(reading: DsmrReading) -> NoReturn:
    """ Publishes a JSON formatted DSMR reading to a broker, if set and enabled. """
    json_settings = telegram.JSONTelegramMQTTSettings.get_solo()

    if not json_settings.enabled:
        return

    # Default to UTC, but allow local timezone on demand (#463).
    if json_settings.use_local_timezone:
        reading.convert_to_local_timezone()

    publish_json_data(topic=json_settings.topic, mapping_format=json_settings.formatting, data_source=reading)


def publish_split_topic_dsmr_reading(reading: DsmrReading) -> NoReturn:
    """ Publishes a DSMR reading to a broker, formatted in a separate topic per field name, if set and enabled. """
    split_topic_settings = telegram.SplitTopicTelegramMQTTSettings.get_solo()

    if not split_topic_settings.enabled:
        return

    # Default to UTC, but allow local timezone on demand (#463).
    if split_topic_settings.use_local_timezone:
        reading.convert_to_local_timezone()

    publish_split_topic_data(mapping_format=split_topic_settings.formatting, data_source=reading)


def publish_day_consumption() -> NoReturn:
    """ Publishes day consumption to a broker, if set and enabled. """
    json_settings = day_totals.JSONDayTotalsMQTTSettings.get_solo()
    split_topic_settings = day_totals.SplitTopicDayTotalsMQTTSettings.get_solo()

    if not json_settings.enabled and not split_topic_settings.enabled:
        return

    try:
        latest_electricity = ElectricityConsumption.objects.all().order_by('-read_at')[0]
    except IndexError:
        # Don't even bother when no data available.
        return

    day_consumption = dsmr_consumption.services.day_consumption(
        day=timezone.localtime(latest_electricity.read_at).date()
    )

    if json_settings.enabled:
        publish_json_data(
            topic=json_settings.topic,
            mapping_format=json_settings.formatting,
            data_source=day_consumption
        )

    if split_topic_settings.enabled:
        publish_split_topic_data(
            mapping_format=split_topic_settings.formatting,
            data_source=day_consumption
        )


def publish_json_period_totals() -> NoReturn:
    """ Publishes JSON formatted period totals to a broker, if set and enabled. """
    json_settings = period_totals.JSONCurrentPeriodTotalsMQTTSettings.get_solo()

    if not json_settings.enabled:
        return

    totals = convert_period_totals()

    if not totals:
        return

    publish_json_data(topic=json_settings.topic, mapping_format=json_settings.formatting, data_source=totals)


def publish_split_topic_period_totals() -> NoReturn:
    """ Publishes period totals to a broker, formatted in a separate topic per field name, if set and enabled. """
    split_topic_settings = period_totals.SplitTopicCurrentPeriodTotalsMQTTSettings.get_solo()

    if not split_topic_settings.enabled:
        return

    totals = convert_period_totals()

    if not totals:
        return

    publish_split_topic_data(mapping_format=split_topic_settings.formatting, data_source=totals)


def convert_period_totals() -> Dict:
    """ Uses a generic datasource, but should be converted to flat format. Also, not all data is required at all. """
    totals = dsmr_stats.services.period_totals()

    excluded_keys = ('number_of_days', 'temperature_avg', 'temperature_min', 'temperature_max')
    result = {}

    for k in totals['month'].keys():
        if k in excluded_keys or totals['month'][k] is None:
            continue

        result['current_month_' + k] = totals['month'][k]

    for k in totals['year'].keys():
        if k in excluded_keys or totals['year'][k] is None:
            continue

        result['current_year_' + k] = totals['year'][k]

    return result


def publish_split_topic_meter_statistics() -> NoReturn:
    """ Publishes meter statistics to a broker, formatted in a separate topic per field name, if set and enabled. """
    split_topic_settings = meter_statistics.SplitTopicMeterStatisticsMQTTSettings.get_solo()

    if not split_topic_settings.enabled:
        return

    publish_split_topic_data(mapping_format=split_topic_settings.formatting, data_source=MeterStatistics.get_solo())


def publish_json_gas_consumption(instance: GasConsumption) -> NoReturn:
    """ Publishes JSON formatted gas consumption to a broker, if set and enabled. """
    json_settings = consumption.JSONGasConsumptionMQTTSettings.get_solo()

    if not json_settings.enabled:
        return

    publish_json_data(topic=json_settings.topic, mapping_format=json_settings.formatting, data_source=instance)


def publish_split_topic_gas_consumption(instance: GasConsumption) -> NoReturn:
    """ Publishes gas consumption to a broker, formatted in a separate topic per field name, if set and enabled. """
    split_topic_settings = consumption.SplitTopicGasConsumptionMQTTSettings.get_solo()

    if not split_topic_settings.enabled:
        return

    publish_split_topic_data(mapping_format=split_topic_settings.formatting, data_source=instance)


def publish_json_data(topic: str, mapping_format: str, data_source) -> NoReturn:
    """ Generic JSON data dispatcher. """
    config_parser = configparser.ConfigParser()
    config_parser.read_string(mapping_format)
    json_mapping = config_parser['mapping']
    json_dict = {}

    # Convert when not yet a dict.
    if not isinstance(data_source, dict):
        data_source = data_source.__dict__

    for k, v in data_source.items():
        if k not in json_mapping:
            continue

        config_key = json_mapping[k]
        json_dict[config_key] = v

    json_data = json.dumps(json_dict, cls=serializers.json.DjangoJSONEncoder)
    dsmr_mqtt.services.messages.queue_message(topic=topic, payload=json_data)


def publish_split_topic_data(mapping_format: str, data_source) -> NoReturn:
    """ Generic split topic data dispatcher. """
    config_parser = configparser.ConfigParser()
    config_parser.read_string(mapping_format)
    split_mapping = config_parser['mapping']

    # Convert when not yet a dict.
    if not isinstance(data_source, dict):
        serialized_data = json.loads(serializers.serialize('json', [data_source]))
        data_source = dict(serialized_data[0]['fields'].items())
        data_source['id'] = serialized_data[0]['pk']

    for k, v in data_source.items():
        if k not in split_mapping:
            continue

        dsmr_mqtt.services.messages.queue_message(topic=split_mapping[k], payload=v)
