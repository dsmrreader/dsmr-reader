from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_mqtt.models.settings import MQTTBrokerSettings, RawTelegramMQTTSettings, JSONTelegramMQTTSettings,\
    SplitTopicTelegramMQTTSettings
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_datalogger.signals
import dsmr_mqtt.services


class TestServices(TestCase):
    def _create_dsmrreading(self):
        return DsmrReading.objects.create(
            timestamp=timezone.now(),
            electricity_delivered_1=1,
            electricity_returned_1=2,
            electricity_delivered_2=3,
            electricity_returned_2=4,
            electricity_currently_delivered=5,
            electricity_currently_returned=6,
        )

    @mock.patch('dsmr_mqtt.services.publish_raw_dsmr_telegram')
    def test_raw_telegram_signal(self, service_mock):
        self.assertFalse(service_mock.called)
        dsmr_datalogger.signals.raw_telegram.send_robust(sender=None, data='test')
        self.assertTrue(service_mock.called)

    @mock.patch('dsmr_mqtt.services.publish_json_dsmr_reading')
    @mock.patch('dsmr_mqtt.services.publish_split_topic_dsmr_reading')
    def test_create_reading_signal(self, *service_mocks):
        self.assertFalse(all([x.called for x in service_mocks]))
        self._create_dsmrreading()
        self.assertTrue(all([x.called for x in service_mocks]))

        # Check exception handling.
        for x in service_mocks:
            x.reset_mock()
            x.side_effect = EnvironmentError('Random error')

        self.assertFalse(all([x.called for x in service_mocks]))
        self._create_dsmrreading()
        self.assertTrue(all([x.called for x in service_mocks]))

        # Check signal for only new models.
        for x in service_mocks:
            x.reset_mock()

        self.assertFalse(all([x.called for x in service_mocks]))
        DsmrReading.objects.all().update(electricity_currently_delivered=10)
        self.assertFalse(all([x.called for x in service_mocks]))

    def test_get_broker_configuration(self):
        broker_settings = MQTTBrokerSettings.get_solo()
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

    @mock.patch('paho.mqtt.publish.single')
    def test_publish_raw_dsmr_telegram(self, mqtt_mock):
        raw_settings = RawTelegramMQTTSettings.get_solo()

        # Disabled by default.
        self.assertFalse(raw_settings.enabled)
        self.assertFalse(mqtt_mock.called)
        dsmr_mqtt.services.publish_raw_dsmr_telegram(data='test')
        self.assertFalse(mqtt_mock.called)

        # Now enabled.
        raw_settings.enabled = True
        raw_settings.save()
        dsmr_mqtt.services.publish_raw_dsmr_telegram(data='test')
        self.assertTrue(mqtt_mock.called)

        # On error.
        mqtt_mock.side_effect = ValueError('Invalid host.')
        dsmr_mqtt.services.publish_raw_dsmr_telegram(data='test')

    @mock.patch('paho.mqtt.publish.single')
    def test_publish_json_dsmr_reading(self, mqtt_mock):
        json_settings = JSONTelegramMQTTSettings.get_solo()
        dsmr_reading = self._create_dsmrreading()

        # Mapping.
        json_settings.formatting = '''
[mapping]
# READING FIELD = JSON FIELD
id = aaa
timestamp = bbb
electricity_delivered_1 = ccc
electricity_returned_1 = ddd
electricity_delivered_2 = eee
electricity_returned_2 = fff
electricity_currently_delivered = ggg
electricity_currently_returned = hhh
phase_currently_delivered_l1 = iii
phase_currently_delivered_l2 = jjj
phase_currently_delivered_l3 = kkk
extra_device_timestamp = lll
extra_device_delivered = mmm
'''
        json_settings.save()

        # Disabled by default.
        self.assertFalse(json_settings.enabled)
        self.assertFalse(mqtt_mock.called)
        dsmr_mqtt.services.publish_json_dsmr_reading(reading=dsmr_reading)
        self.assertFalse(mqtt_mock.called)

        # Now enabled.
        json_settings.enabled = True
        json_settings.save()
        dsmr_mqtt.services.publish_json_dsmr_reading(reading=dsmr_reading)
        self.assertTrue(mqtt_mock.called)

        # On error.
        mqtt_mock.side_effect = ValueError('Invalid host.')
        dsmr_mqtt.services.publish_json_dsmr_reading(reading=dsmr_reading)

    @mock.patch('paho.mqtt.publish.multiple')
    def test_publish_split_topic_dsmr_reading(self, mqtt_mock):
        split_topic_settings = SplitTopicTelegramMQTTSettings.get_solo()
        dsmr_reading = self._create_dsmrreading()

        # Mapping.
        split_topic_settings.formatting = '''
[mapping]
# READING FIELD = TOPIC PATH
id = dsmr/telegram/id
timestamp = dsmr/telegram/timestamp
electricity_delivered_1 = dsmr/telegram/electricity_delivered_1
electricity_returned_1 = dsmr/telegram/electricity_returned_1
electricity_delivered_2 = dsmr/telegram/electricity_delivered_2
electricity_returned_2 = dsmr/telegram/electricity_returned_2
electricity_currently_delivered = dsmr/telegram/electricity_currently_delivered
electricity_currently_returned = dsmr/telegram/electricity_currently_returned
phase_currently_delivered_l1 = dsmr/telegram/phase_currently_delivered_l1
phase_currently_delivered_l2 = dsmr/telegram/phase_currently_delivered_l2
phase_currently_delivered_l3 = dsmr/telegram/phase_currently_delivered_l3
extra_device_timestamp = dsmr/telegram/extra_device_timestamp
extra_device_delivered = dsmr/telegram/extra_device_delivered
'''
        split_topic_settings.save()

        # Disabled by default.
        self.assertFalse(split_topic_settings.enabled)
        self.assertFalse(mqtt_mock.called)
        dsmr_mqtt.services.publish_split_topic_dsmr_reading(reading=dsmr_reading)
        self.assertFalse(mqtt_mock.called)

        # Now enabled.
        split_topic_settings.enabled = True
        split_topic_settings.save()
        dsmr_mqtt.services.publish_split_topic_dsmr_reading(reading=dsmr_reading)
        self.assertTrue(mqtt_mock.called)

        # On error.
        mqtt_mock.side_effect = ValueError('Invalid host.')
        dsmr_mqtt.services.publish_split_topic_dsmr_reading(reading=dsmr_reading)
