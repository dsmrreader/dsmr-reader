import configparser
import logging
import json

from django.core import serializers
import paho.mqtt.publish as publish

from dsmr_mqtt.models.settings import MQTTBrokerSettings, RawTelegramMQTTSettings, JSONTelegramMQTTSettings,\
    SplitTopicTelegramMQTTSettings


logger = logging.getLogger('dsmrreader')


def get_broker_configuration():
    """ Returns the broker configuration from the settings, in dict format, ready to use with paho.mqtt. """
    broker_settings = MQTTBrokerSettings.get_solo()

    kwargs = {
        'hostname': broker_settings.hostname,
        'port': broker_settings.port,
        'client_id': broker_settings.client_id,
        'auth': None,
    }

    if broker_settings.username and broker_settings.password:
        kwargs.update({
            'auth': {
                'username': broker_settings.username,
                'password': broker_settings.password,
            }
        })

    return kwargs


def publish_raw_dsmr_telegram(data):
    """ Publishes a raw DSMR telegram string to a broker, if set and enabled. """
    raw_settings = RawTelegramMQTTSettings.get_solo()

    if not raw_settings.enabled:
        return

    broker_kwargs = get_broker_configuration()

    try:
        publish.single(topic=raw_settings.topic, payload=data, **broker_kwargs)
    except ValueError as error:
        logger.error('MQTT publish_raw_dsmr_telegram() | {}'.format(error))


def publish_json_dsmr_reading(reading):
    """ Publishes a JSON formatted DSMR reading to a broker, if set and enabled. """
    json_settings = JSONTelegramMQTTSettings.get_solo()

    if not json_settings.enabled:
        return

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
    broker_kwargs = get_broker_configuration()

    try:
        publish.single(topic=json_settings.topic, payload=json_reading, **broker_kwargs)
    except ValueError as error:
        logger.error('MQTT publish_json_dsmr_reading() | {}'.format(error))


def publish_split_topic_dsmr_reading(reading):
    """ Publishes a DSMR reading to a broker, formatted in multiple topic per field name, if set and enabled. """
    split_topic_settings = SplitTopicTelegramMQTTSettings.get_solo()

    if not split_topic_settings.enabled:
        return

    # User specified formatting.
    config_parser = configparser.ConfigParser()
    config_parser.read_string(split_topic_settings.formatting)
    topic_mapping = config_parser['mapping']

    mqtt_messages = []
    serialized_reading = json.loads(serializers.serialize('json', [reading]))
    reading_fields = dict(serialized_reading[0]['fields'].items())
    reading_fields['id'] = serialized_reading[0]['pk']

    # Copy all fields described in the mapping.
    for k, v in reading_fields.items():
        if k not in topic_mapping:
            continue

        mqtt_messages.append({
            'topic': topic_mapping[k],
            'payload': v,
        })

    broker_kwargs = get_broker_configuration()

    try:
        publish.multiple(msgs=mqtt_messages, **broker_kwargs)
    except ValueError as error:
        logger.error('MQTT publish_split_topic_dsmr_reading() | {}'.format(error))
