import logging
import ssl

from django.conf import settings
import paho.mqtt.client as paho

from dsmr_backend.signals import backend_restart_required
from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
from dsmr_mqtt.models import queue


logger = logging.getLogger('dsmrreader')


def initialize_client():
    """ Initializes the MQTT client and returns client instance. """
    broker_settings = MQTTBrokerSettings.get_solo()

    if not broker_settings.enabled:
        return logger.debug('MQTT: Integration disabled in settings (or it was disabled due to a configuration error)')

    if not broker_settings.hostname:
        logger.error('MQTT: No hostname found in settings, disabling MQTT')
        broker_settings.update(enabled=False)
        raise RuntimeError('No hostname found in settings')

    logger.debug('MQTT: Initializing MQTT client for "%s:%d"', broker_settings.hostname, broker_settings.port)
    mqtt_client = paho.Client(client_id=broker_settings.client_id)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_log = on_log

    if broker_settings.username:
        mqtt_client.username_pw_set(broker_settings.username, broker_settings.password)

    # SSL/TLS.
    if broker_settings.secure == MQTTBrokerSettings.SECURE_CERT_NONE:
        logger.debug('MQTT: Using secure connection (ssl.CERT_NONE)')
        mqtt_client.tls_set(cert_reqs=ssl.CERT_NONE)
    elif broker_settings.secure == MQTTBrokerSettings.SECURE_CERT_REQUIRED:
        logger.debug('MQTT: Using secure connection (ssl.CERT_REQUIRED)')
        mqtt_client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
    else:
        logger.debug('MQTT: Using insecure connection (no TLS)')

    try:
        mqtt_client.connect(host=broker_settings.hostname, port=broker_settings.port)
    except Exception as error:
        logger.error(
            'MQTT: Failed to connect to broker (%s:%d): %s',
            broker_settings.hostname,
            broker_settings.port,
            error
        )
        signal_reconnect()
        raise RuntimeError('MQTT: Failed to connect to broker')

    return mqtt_client


def run(mqtt_client):
    """ Reads any messages from the queue and publishing them to the MQTT broker. """
    broker_settings = MQTTBrokerSettings.get_solo()

    # Keep batches small, only send the latest X messages. The rest will be trimmed (in case of delay).
    message_queue = queue.Message.objects.all().order_by('-pk')[0:settings.DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE]

    if not message_queue:
        return

    logger.info('MQTT: Processing %d message(s)', len(message_queue))

    for current in message_queue:
        logger.debug('MQTT: Publishing message (#%s) for %s: %s', current.pk, current.topic, current.payload)
        mqtt_client.publish(
            topic=current.topic,
            payload=current.payload,
            qos=broker_settings.qos,
            retain=True
        )

        logger.debug('MQTT: Deleting published message (#%s)', current.pk)
        current.delete()

    # Delete any overflow in messages.
    queue.Message.objects.all().delete()

    # Networking.
    mqtt_client.loop(0.1)

    # We cannot raise any exception in callbacks, this is our check point. This MUST be called AFTER the first loop().
    if not mqtt_client.is_connected():
        signal_reconnect()
        raise RuntimeError('MQTT: Client no longer connected')


def signal_reconnect():
    backend_restart_required.send_robust(None)
    logger.warning('MQTT: Client no longer connected. Signaling restart to reconnect...')


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
    logger.debug('MQTT: Paho client: on_connect(userdata, flags, rc) %s %s %s', userdata, flags, rc)

    try:
        logger.debug('MQTT: --- %s : %s -> %s', client._host, client._port, RC_MAPPING[rc])
    except KeyError:
        pass


def on_disconnect(client, userdata, rc):
    """ MQTT client callback for disconnecting. Outputs some debug logging. """

    """
    From the docs, rc value:
        If MQTT_ERR_SUCCESS (0), the callback was called in response to a disconnect() call.
        If any other value the disconnection was unexpected, such as might be caused by a network error.
    """
    logger.debug('MQTT: Paho client: on_disconnect(userdata, rc) %s %s', userdata, rc)

    if rc != paho.MQTT_ERR_SUCCESS:
        logger.warning('MQTT: --- Unexpected disconnect, re-connecting...')

        try:
            client.reconnect()
        except Exception as error:
            logger.error('MQTT: Failed to re-connect to broker: %s', error)
            client.disconnect()  # We cannot throw an exception here, so abort gracefully.


def on_log(client, userdata, level, buf):
    """ MQTT client callback for logging. Outputs some debug logging. """
    logger.debug('MQTT: Paho client: on_log(userdata, level, buf) %s %s %s', userdata, level, buf)
