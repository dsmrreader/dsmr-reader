import logging

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from dsmr_backend.mixins import InfiniteManagementCommandMixin, StopInfiniteRun
from dsmr_client.models import ContinuousClientSettings
from dsmr_influxdb.models import InfluxdbIntegrationSettings
from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
import dsmr_mqtt.services.broker
import dsmr_influxdb.services

logger = logging.getLogger('commands')


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Continuous client for publishing data to external services, when enabled.')
    name = __name__  # Required for PID file.

    # Global during this process' lifetime.
    mqtt_client = None
    influxdb_client = None

    def initialize(self):
        """ Set up continuous client(s). """
        self.sleep_time = ContinuousClientSettings.get_solo().process_sleep

        # MQTT
        if MQTTBrokerSettings.get_solo().enabled:
            try:
                self.mqtt_client = dsmr_mqtt.services.broker.initialize_client()
            except RuntimeError:
                logger.error('CLIENT | Failed to initialize MQTT client')
        else:
            logger.info('CLIENT | MQTT integration not enabled')

        # InfluxDB
        if InfluxdbIntegrationSettings.get_solo().enabled:
            try:
                self.influxdb_client = dsmr_influxdb.services.initialize_client()
            except RuntimeError:
                logger.error('CLIENT | Failed to initialize InfluxDB client')
        else:
            logger.info('CLIENT | InfluxDB integration not enabled')

    def shutdown(self):
        """ Disconnects the client(s) gracefully. """
        if self.mqtt_client:
            self.mqtt_client.disconnect()

        if self.influxdb_client:
            self.influxdb_client.close()

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        if self.mqtt_client:
            logger.debug('CLIENT | Running MQTT client')
            dsmr_mqtt.services.broker.run(mqtt_client=self.mqtt_client)

        if self.influxdb_client:
            logger.debug('CLIENT | Running InfluxDB client')
            dsmr_influxdb.services.run(influxdb_client=self.influxdb_client)

        if ContinuousClientSettings.get_solo().restart_required:
            ContinuousClientSettings.objects.update(restart_required=False)
            logger.warning('CLIENT | --- Detected restart required, stopping process...')
            raise StopInfiniteRun()
