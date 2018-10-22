import logging

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
import django.db.models.signals

import dsmr_datalogger.signals


logger = logging.getLogger('dsmrreader')


class AppConfig(AppConfig):
    # All imports below prevents an AppRegistryNotReady error on Django init.
    name = 'dsmr_mqtt'
    verbose_name = _('MQTT')

    def ready(self):
        from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
        from dsmr_datalogger.models.reading import DsmrReading

        dsmr_datalogger.signals.raw_telegram.connect(
            receiver=self._on_raw_telegram_signal,
            dispatch_uid=self.__class__
        )
        django.db.models.signals.post_save.connect(
            receiver=self._on_dsmrreading_created_signal,
            dispatch_uid=self.__class__,
            sender=DsmrReading
        )
        django.db.models.signals.post_save.connect(
            receiver=self._on_broker_settings_updated_signal,
            dispatch_uid=self.__class__,
            sender=MQTTBrokerSettings
        )

        # Required for model detection.
        import dsmr_mqtt.models.queue  # noqa

    def _on_raw_telegram_signal(self, data, **kwargs):
        import dsmr_mqtt.services.callbacks
        dsmr_mqtt.services.callbacks.publish_raw_dsmr_telegram(data=data)

    def _on_broker_settings_updated_signal(self, instance, created, raw, update_fields, **kwargs):
        # Skip new or imported (fixture) instances. And do not update if this hook has just updated it.
        if created or raw or (update_fields and 'restart_required' in update_fields):
            return

        from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
        broker_settings = MQTTBrokerSettings.get_solo()
        broker_settings.restart_required = True
        broker_settings.save(update_fields=['restart_required'])  # DO NOT CHANGE: Keep this save() + update_fields.

    def _on_dsmrreading_created_signal(self, instance, created, raw, **kwargs):
        # Skip new or imported (fixture) instances.
        if not created or raw:
            return

        import dsmr_mqtt.services.callbacks

        try:
            dsmr_mqtt.services.callbacks.publish_json_dsmr_reading(reading=instance)
        except Exception as error:
            logger.error('publish_json_dsmr_reading() failed: {}'.format(error))

        try:
            dsmr_mqtt.services.callbacks.publish_split_topic_dsmr_reading(reading=instance)
        except Exception as error:
            logger.error('publish_split_topic_dsmr_reading() failed: {}'.format(error))

        try:
            dsmr_mqtt.services.callbacks.publish_day_consumption()
        except Exception as error:
            logger.error('publish_day_consumption() failed: {}'.format(error))

        try:
            dsmr_mqtt.services.callbacks.publish_split_topic_meter_statistics()
        except Exception as error:
            logger.error('publish_split_topic_meter_statistics() failed: {}'.format(error))
