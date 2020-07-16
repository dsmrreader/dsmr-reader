import logging

from django.apps import AppConfig
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from influxdb import InfluxDBClient
import django.db.models.signals

from dsmr_backend.signals import initialize_persistent_client, run_persistent_client, terminate_persistent_client


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


@receiver(initialize_persistent_client)
def on_initialize_persistent_client(**kwargs):
    import dsmr_influxdb.services
    return dsmr_influxdb.services.initialize_client()


@receiver(run_persistent_client)
def on_run_persistent_client(client, **kwargs):
    if not isinstance(client, InfluxDBClient):
        return

    import dsmr_influxdb.services
    dsmr_influxdb.services.run(client)


@receiver(terminate_persistent_client)
def on_terminate_persistent_client(client, **kwargs):
    if not isinstance(client, InfluxDBClient):
        return

    client.close()
