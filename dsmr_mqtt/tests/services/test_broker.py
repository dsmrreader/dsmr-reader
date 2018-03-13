from django.test import TestCase

from dsmr_mqtt.models.settings import broker
import dsmr_mqtt.services


class TestBroker(TestCase):
    def test_get_broker_configuration(self):
        broker_settings = broker.MQTTBrokerSettings.get_solo()
        broker_dict = dsmr_mqtt.services.get_broker_configuration()

        self.assertEqual(broker_dict['hostname'], broker_settings.hostname)
        self.assertEqual(broker_dict['port'], broker_settings.port)
        self.assertEqual(broker_dict['client_id'], broker_settings.client_id)
        self.assertIsNone(broker_dict['auth'])

        broker_settings.username = 'user'
        broker_settings.password = 'pass'
        broker_settings.save()

        broker_dict = dsmr_mqtt.services.get_broker_configuration()
        self.assertEqual(broker_dict['auth']['username'], broker_settings.username)
        self.assertEqual(broker_dict['auth']['password'], broker_settings.password)
