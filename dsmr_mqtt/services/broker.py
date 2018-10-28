import logging
import time
import ssl

from django.conf import settings
import paho.mqtt.client as paho

from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
from dsmr_mqtt.models import queue
from dsmr_backend.mixins import StopInfiniteRun


logger = logging.getLogger('commands')


def initialize():
    """ Initializes the MQTT client and returns client instance. """
    broker_settings = MQTTBrokerSettings.get_solo()

    if not broker_settings.hostname:
        logger.warning('MQTT | No hostname found in settings, retrying in a minute...')
        time.sleep(60)
        return initialize()

    mqtt_client = paho.Client(client_id=broker_settings.client_id)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect

    if broker_settings.debug:
        mqtt_client.on_log = on_log
        mqtt_client.on_publish = on_publish

    if broker_settings.username:
        mqtt_client.username_pw_set(broker_settings.username, broker_settings.password)

    # SSL/TLS.
    if broker_settings.secure == MQTTBrokerSettings.SECURE_CERT_NONE:
        logger.debug('MQTT | Initializing secure connection (ssl.CERT_NONE)')
        mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
    elif broker_settings.secure == MQTTBrokerSettings.SECURE_CERT_REQUIRED:
        logger.debug('MQTT | Initializing secure connection (ssl.CERT_REQUIRED)')
        mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    else:
        logger.debug('MQTT | Initializing insecure connection (no TLS)')

    try:
        mqtt_client.connect(host=broker_settings.hostname, port=broker_settings.port)
    except Exception as error:
        logger.error('MQTT | Failed to connect to broker, restarting in a minute: %s', error)
        time.sleep(60)
        raise StopInfiniteRun()

    return mqtt_client


def run(mqtt_client):
    """ Reads any messages from the queue and publishing them to the MQTT broker. """
    mqtt_client.loop()

    broker_settings = MQTTBrokerSettings.get_solo()

    # Keep batches small, only send the latest X messages. The rest will be purged (in case of delay).
    message_queue = queue.Message.objects.all().order_by('-pk')[0:settings.DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE]

    for current in message_queue:
        mqtt_client.publish(
            topic=current.topic,
            payload=current.payload,
            qos=broker_settings.qos
        )
        current.delete()

    # Delete any overflow in messages.
    queue.Message.objects.all().delete()


def on_connect(client, userdata, flags, rc):
    """ MQTT client callback for connecting. Outputs some debug logging. """
    # From the docs, rc values:
    RC_MAPPING = {
        0: 'Connection successful',
        1: 'Connection refused - incorrect protocol version',
        2: 'Connection refused - invalid client identifier',
        3: 'Connection refused - server unavailable',
        4: 'Connection refused - bad username or password',
        5: 'Connection refused - not authorised',
    }
    logger.debug('MQTT | Paho client: on_connect(userdata, flags, rc) %s %s %s', userdata, flags, rc)

    try:
        logger.debug('MQTT | --- %s : %s -> %s'.format(client._host, client._port, RC_MAPPING[rc]))
    except KeyError:
        pass


def on_disconnect(client, userdata, rc):
    """ MQTT client callback for disconnecting. Outputs some debug logging. """
    """
    From the docs, rc value:
        If MQTT_ERR_SUCCESS (0), the callback was called in response to a disconnect() call.
        If any other value the disconnection was unexpected, such as might be caused by a network error.
    """
    logger.debug('MQTT | Paho client: on_disconnect(userdata, rc) %s %s', userdata, rc)

    if rc != paho.MQTT_ERR_SUCCESS:
        logger.warning('MQTT | --- Unexpected disconnect, re-connecting...')

        try:
            client.reconnect()
        except Exception as error:
            logger.error('MQTT | Failed to re-connect to broker: %s', error)
            raise StopInfiniteRun()  # Don't bother even to continue, just reset everything.


def on_log(client, userdata, level, buf):
    """ MQTT client callback for logging. Outputs some debug logging. """
    logger.debug('MQTT | Paho client: on_log(userdata, level, buf) %s %s %s', userdata, level, buf)


def on_publish(client, userdata, mid):
    """ MQTT client callback for publishing. Outputs some debug logging. """
    logger.debug('MQTT | Paho client: on_publish(userdata, mid) %s %s', userdata, mid)
