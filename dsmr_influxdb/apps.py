import logging

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import django.db.models.signals


logger = logging.getLogger('dsmrreader')


class DsmrInfluxdbConfig(AppConfig):
    name = 'dsmr_influxdb'
    verbose_name = _('InfluxDB')

    def ready(self):
        from dsmr_datalogger.models.reading import DsmrReading

        django.db.models.signals.post_save.connect(
            receiver=self._on_dsmrreading_created_signal,
            dispatch_uid=self.__class__,
            sender=DsmrReading
        )

    def _on_dsmrreading_created_signal(self, instance, created, raw, **kwargs):
        # Skip existing or imported (fixture) instances.
        if not created or raw:
            return

        import dsmr_influxdb.services

        try:
            dsmr_influxdb.services.publish_dsmr_reading(instance=instance)
        except Exception as error:
            logger.error('publish_dsmr_reading() failed: %s', error)
