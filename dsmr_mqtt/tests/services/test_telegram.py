from unittest import mock
import json

from django.test import TestCase
from django.utils import timezone

from dsmr_mqtt.models.settings import telegram
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
            phase_currently_delivered_l1=0.25,
            phase_currently_delivered_l2=0.35,
            phase_currently_delivered_l3=0.3,
            phase_currently_returned_l1=0.5,
            phase_currently_returned_l2=0.75,
            phase_currently_returned_l3=1.25,
            extra_device_timestamp=timezone.now() + timezone.timedelta(hours=12)
        )


class TestTelegramAndReading(TestServices):
    @mock.patch('dsmr_mqtt.services.publish_raw_dsmr_telegram')
    def test_raw_telegram_signal(self, service_mock):
        self.assertFalse(service_mock.called)
        dsmr_datalogger.signals.raw_telegram.send_robust(sender=None, data='test')
        self.assertTrue(service_mock.called)

    @mock.patch('dsmr_mqtt.services.publish_json_dsmr_reading')
    @mock.patch('dsmr_mqtt.services.publish_split_topic_dsmr_reading')
    @mock.patch('dsmr_mqtt.services.publish_day_totals')
    @mock.patch('dsmr_mqtt.services.publish_split_topic_meter_statistics')
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

    @mock.patch('paho.mqtt.publish.single')
    def test_publish_raw_dsmr_telegram(self, mqtt_mock):
        raw_settings = telegram.RawTelegramMQTTSettings.get_solo()

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

    @mock.patch('paho.mqtt.publish.multiple')
    @mock.patch('django.utils.timezone.now')
    def test_publish_json_dsmr_reading(self, now_mock, mqtt_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2018, 1, 1), timezone=timezone.utc
        )
        json_settings = telegram.JSONTelegramMQTTSettings.get_solo()
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
phase_currently_returned_l1 = lll
phase_currently_returned_l2 = mmm
phase_currently_returned_l3 = nnn
extra_device_timestamp = ooo
extra_device_delivered = ppp
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

        _, args, _ = mqtt_mock.mock_calls[0]
        payload = json.loads(args[0][0]['payload'])

        self.assertEqual(payload['aaa'], DsmrReading.objects.get().pk)
        self.assertEqual(payload['bbb'], '2018-01-01T00:00:00Z')
        self.assertEqual(payload['ccc'], 1)
        self.assertEqual(payload['ddd'], 2)
        self.assertEqual(payload['eee'], 3)
        self.assertEqual(payload['fff'], 4)
        self.assertEqual(payload['ggg'], 5)
        self.assertEqual(payload['hhh'], 6)
        self.assertEqual(payload['iii'], 0.25)
        self.assertEqual(payload['jjj'], 0.35)
        self.assertEqual(payload['kkk'], 0.3)
        self.assertEqual(payload['lll'], 0.5)
        self.assertEqual(payload['mmm'], 0.75)
        self.assertEqual(payload['nnn'], 1.25)
        self.assertEqual(payload['ooo'], '2018-01-01T12:00:00Z')
        self.assertIsNone(payload['ppp'])

        # Check timezone conversion.
        telegram.JSONTelegramMQTTSettings.objects.update(use_local_timezone=True)
        mqtt_mock.reset_mock()

        dsmr_mqtt.services.publish_json_dsmr_reading(reading=dsmr_reading)
        _, args, _ = mqtt_mock.mock_calls[0]
        payload = json.loads(args[0][0]['payload'])
        self.assertEqual(payload['bbb'], '2018-01-01T01:00:00+01:00')  # No longer UTC.
        self.assertEqual(payload['ooo'], '2018-01-01T13:00:00+01:00')  # No longer UTC.

        # On error.
        mqtt_mock.side_effect = ValueError('Invalid host.')
        dsmr_mqtt.services.publish_json_dsmr_reading(reading=dsmr_reading)

    @mock.patch('paho.mqtt.publish.multiple')
    @mock.patch('django.utils.timezone.now')
    def test_publish_split_topic_dsmr_reading(self, now_mock, mqtt_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2018, 1, 1), timezone=timezone.utc
        )
        split_topic_settings = telegram.SplitTopicTelegramMQTTSettings.get_solo()
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
phase_currently_returned_l1 = dsmr/telegram/phase_currently_returned_l1
phase_currently_returned_l2 = dsmr/telegram/phase_currently_returned_l2
phase_currently_returned_l3 = dsmr/telegram/phase_currently_returned_l3
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

        # Assert timezone UTC for this test.
        _, _, kwargs = mqtt_mock.mock_calls[0]
        expected = {
            'payload': '2018-01-01T00:00:00Z',
            'topic': 'dsmr/telegram/timestamp'
        }
        self.assertIn(expected, kwargs['msgs'])
        expected = {
            'payload': '2018-01-01T12:00:00Z',
            'topic': 'dsmr/telegram/extra_device_timestamp'
        }
        self.assertIn(expected, kwargs['msgs'])

        # Check timezone conversion.
        telegram.SplitTopicTelegramMQTTSettings.objects.update(use_local_timezone=True)
        mqtt_mock.reset_mock()

        dsmr_mqtt.services.publish_split_topic_dsmr_reading(reading=dsmr_reading)
        _, _, kwargs = mqtt_mock.mock_calls[0]
        expected = {
            'payload': '2018-01-01T01:00:00+01:00',  # No longer UTC.
            'topic': 'dsmr/telegram/timestamp'
        }
        self.assertIn(expected, kwargs['msgs'])
        expected = {
            'payload': '2018-01-01T13:00:00+01:00',  # No longer UTC.
            'topic': 'dsmr/telegram/extra_device_timestamp'
        }
        self.assertIn(expected, kwargs['msgs'])

        # On error.
        mqtt_mock.side_effect = ValueError('Invalid host.')
        dsmr_mqtt.services.publish_split_topic_dsmr_reading(reading=dsmr_reading)
