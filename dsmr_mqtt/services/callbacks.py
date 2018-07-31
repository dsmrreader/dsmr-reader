import configparser
import json

from django.core import serializers
from django.utils import timezone

from dsmr_mqtt.models.settings import day_totals, telegram, meter_statistics
from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_mqtt.models import queue
import dsmr_consumption.services


def publish_raw_dsmr_telegram(data):
    """ Publishes a raw DSMR telegram string to a broker, if set and enabled. """
    raw_settings = telegram.RawTelegramMQTTSettings.get_solo()

    if not raw_settings.enabled:
        return

    queue.Message.objects.create(topic=raw_settings.topic, payload=data)


def publish_json_dsmr_reading(reading):
    """ Publishes a JSON formatted DSMR reading to a broker, if set and enabled. """
    json_settings = telegram.JSONTelegramMQTTSettings.get_solo()

    if not json_settings.enabled:
        return

    # Default to UTC, but allow local timezone on demand (#463).
    if json_settings.use_local_timezone:
        reading.convert_to_local_timezone()

    # User specified formatting.
    config_parser = configparser.ConfigParser()
    config_parser.read_string(json_settings.formatting)
    json_mapping = config_parser['mapping']
    json_dict = {}

    # Copy all fields described in the mapping.
    for k, v in reading.__dict__.items():
        if k not in json_mapping:
            continue

        config_key = json_mapping[k]
        json_dict[config_key] = v

    json_reading = json.dumps(json_dict, cls=serializers.json.DjangoJSONEncoder)
    queue.Message.objects.create(topic=json_settings.topic, payload=json_reading)


def publish_split_topic_dsmr_reading(reading):
    """ Publishes a DSMR reading to a broker, formatted in a separate topic per field name, if set and enabled. """
    split_topic_settings = telegram.SplitTopicTelegramMQTTSettings.get_solo()

    if not split_topic_settings.enabled:
        return

    # Default to UTC, but allow local timezone on demand (#463).
    if split_topic_settings.use_local_timezone:
        reading.convert_to_local_timezone()

    # User specified formatting.
    config_parser = configparser.ConfigParser()
    config_parser.read_string(split_topic_settings.formatting)
    topic_mapping = config_parser['mapping']

    serialized_reading = json.loads(serializers.serialize('json', [reading]))
    reading_fields = dict(serialized_reading[0]['fields'].items())
    reading_fields['id'] = serialized_reading[0]['pk']

    # Copy all fields described in the mapping.
    for k, v in reading_fields.items():
        if k not in topic_mapping:
            continue

        queue.Message.objects.create(topic=topic_mapping[k], payload=v)


def publish_day_consumption():
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
        day_totals_as_json(day_consumption, json_settings)

    if split_topic_settings.enabled:
        day_totals_per_topic(day_consumption, split_topic_settings)


def day_totals_as_json(day_consumption, json_settings):
    """ Converts day consumption to JSON format. """
    config_parser = configparser.ConfigParser()
    config_parser.read_string(json_settings.formatting)
    json_mapping = config_parser['mapping']
    json_dict = {}

    # Use mapping to setup fields for JSON message.
    for k, v in day_consumption.items():
        if k not in json_mapping:
            continue

        config_key = json_mapping[k]
        json_dict[config_key] = v

    json_data = json.dumps(json_dict, cls=serializers.json.DjangoJSONEncoder)
    queue.Message.objects.create(topic=json_settings.topic, payload=json_data)


def day_totals_per_topic(day_consumption, split_topic_settings):
    """ Converts day consumption to split topic messages. """
    config_parser = configparser.ConfigParser()
    config_parser.read_string(split_topic_settings.formatting)
    topic_mapping = config_parser['mapping']

    # Use mapping to setup fields for each message/topic.
    for k, v in day_consumption.items():
        if k not in topic_mapping:
            continue

        queue.Message.objects.create(topic=topic_mapping[k], payload=v)


def publish_split_topic_meter_statistics():
    """ Publishes meter statistics to a broker, formatted in a separate topic per field name, if set and enabled. """
    split_topic_settings = meter_statistics.SplitTopicMeterStatisticsMQTTSettings.get_solo()

    if not split_topic_settings.enabled:
        return

    # User specified formatting.
    config_parser = configparser.ConfigParser()
    config_parser.read_string(split_topic_settings.formatting)
    topic_mapping = config_parser['mapping']

    serialized_reading = json.loads(serializers.serialize('json', [MeterStatistics.get_solo()]))
    reading_fields = dict(serialized_reading[0]['fields'].items())
    reading_fields['id'] = serialized_reading[0]['pk']

    # Copy all fields described in the mapping.
    for k, v in reading_fields.items():
        if k not in topic_mapping:
            continue

        queue.Message.objects.create(topic=topic_mapping[k], payload=v)
