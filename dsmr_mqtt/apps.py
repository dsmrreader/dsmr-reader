import logging

from django.apps import AppConfig
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from paho.mqtt.client import Client
import django.db.models.signals

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_datalogger.signals import raw_telegram, dsmr_reading_created
from dsmr_backend.signals import initialize_persistent_client, run_persistent_client, terminate_persistent_client, \
    request_status

logger = logging.getLogger('dsmrreader')


class MqttAppConfig(AppConfig):
    # All imports below prevents an AppRegistryNotReady error on Django init.
    name = 'dsmr_mqtt'
    verbose_name = _('MQTT')

    def ready(self):
        from dsmr_consumption.models.consumption import GasConsumption

        raw_telegram.connect(
            receiver=self._on_raw_telegram_signal,
            dispatch_uid=self.__class__
        )
        django.db.models.signals.post_save.connect(
            receiver=self._on_gas_consumption_created_signal,
            dispatch_uid=self.__class__,
            sender=GasConsumption
        )
        # Required for model detection.
        import dsmr_mqtt.models.queue  # noqa

    def _on_raw_telegram_signal(self, data, **kwargs):
        import dsmr_mqtt.services.callbacks
        dsmr_mqtt.services.callbacks.publish_raw_dsmr_telegram(data=data)

    def _on_gas_consumption_created_signal(self, instance, created, raw, **kwargs):
        # Skip existing or imported (fixture) instances.
        if not created or raw:
            return

        import dsmr_mqtt.services.callbacks

        # Force local timezone.
        instance.read_at = timezone.localtime(instance.read_at)

        try:
            dsmr_mqtt.services.callbacks.publish_json_gas_consumption(instance=instance)
        except Exception as error:
            logger.error('publish_json_gas_consumption() failed: %s', error)

        try:
            dsmr_mqtt.services.callbacks.publish_split_topic_gas_consumption(instance=instance)
        except Exception as error:
            logger.error('publish_split_topic_gas_consumption() failed: %s', error)


@receiver(dsmr_reading_created)
def _on_dsmrreading_created_signal(instance, **kwargs):
    from dsmr_datalogger.models.reading import DsmrReading

    # Refresh from database, as some decimal fields are strings (?) and mess up formatting. (#733)
    instance = DsmrReading.objects.get(pk=instance.pk)

    import dsmr_mqtt.services.callbacks

    try:
        dsmr_mqtt.services.callbacks.publish_json_dsmr_reading(reading=instance)
    except Exception as error:
        logger.error('publish_json_dsmr_reading() failed: %s', error)

    try:
        dsmr_mqtt.services.callbacks.publish_split_topic_dsmr_reading(reading=instance)
    except Exception as error:
        logger.error('publish_split_topic_dsmr_reading() failed: %s', error)

    try:
        dsmr_mqtt.services.callbacks.publish_day_consumption()
    except Exception as error:
        logger.error('publish_day_consumption() failed: %s', error)

    try:
        dsmr_mqtt.services.callbacks.publish_split_topic_meter_statistics()
    except Exception as error:
        logger.error('publish_split_topic_meter_statistics() failed: %s', error)


@receiver(initialize_persistent_client)
def on_initialize_persistent_client(**kwargs):
    import dsmr_mqtt.services.broker
    return dsmr_mqtt.services.broker.initialize_client()


@receiver(run_persistent_client)
def on_run_persistent_client(client, **kwargs):
    if not isinstance(client, Client):
        return

    import dsmr_mqtt.services.broker
    dsmr_mqtt.services.broker.run(client)


@receiver(terminate_persistent_client)
def on_terminate_persistent_client(client, **kwargs):
    if not isinstance(client, Client):
        return

    client.disconnect()


@receiver(request_status)
def check_mqtt_messages_queue(**kwargs):
    from dsmr_mqtt.models.queue import Message

    if Message.objects.count() < settings.DSMRREADER_MQTT_MAX_MESSAGES_IN_QUEUE:
        return

    return MonitoringStatusIssue(
        __name__,
        _('Too many outgoing MQTT messages queued for transit'),
        timezone.now()
    )
