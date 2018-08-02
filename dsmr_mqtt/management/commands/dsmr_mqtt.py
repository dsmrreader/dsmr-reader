from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.conf import settings

from dsmr_backend.mixins import InfiniteManagementCommandMixin, StopInfiniteRun
from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
import dsmr_mqtt.services.broker


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Dedicated MQTT client for publishing messages to the broker.')
    name = __name__  # Required for PID file.
    sleep_time = settings.DSMRREADER_MQTT_SLEEP

    # Global during this process' lifetime.
    mqtt_client = None

    def initialize(self):
        """ Set up persistent MQTT client. """
        self.mqtt_client = dsmr_mqtt.services.broker.initialize()

    def shutdown(self):
        """ Disconnects the MQTT client gracefully. """
        if self.mqtt_client:
            self.mqtt_client.disconnect()

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        broker_settings = MQTTBrokerSettings.get_solo()

        # Check on each run. In case MQTT was either disabled, enabled or settings were changed.
        if broker_settings.restart_required:
            MQTTBrokerSettings.objects.update(restart_required=False)
            print('MQTT | --- Detected settings change, requiring process restart, stopping...')
            raise StopInfiniteRun()

        dsmr_mqtt.services.broker.run(mqtt_client=self.mqtt_client)
