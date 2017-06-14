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

    def _on_raw_telegram_signal(self, sender, data, **kwargs):
        import dsmr_mqtt.services
        dsmr_mqtt.services.publish_raw_dsmr_telegram(data=data)

    def _on_dsmrreading_created_signal(self, sender, instance, created, **kwargs):
        if not created:
            return

        import dsmr_mqtt.services

        try:
            dsmr_mqtt.services.publish_json_dsmr_reading(reading=instance)
        except Exception as error:
            logger.error('publish_json_dsmr_reading() failed: {}'.format(error))

        try:
            dsmr_mqtt.services.publish_split_topic_dsmr_reading(reading=instance)
        except Exception as error:
            logger.error('publish_split_topic_dsmr_reading() failed: {}'.format(error))
