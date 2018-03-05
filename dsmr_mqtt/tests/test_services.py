from unittest import mock
import json

from django.test import TestCase
from django.utils import timezone

from dsmr_mqtt.models import settings
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
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
    @mock.patch('dsmr_mqtt.services.publish_json_day_totals_overview')
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
        broker_settings = settings.MQTTBrokerSettings.get_solo()
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
        raw_settings = settings.RawTelegramMQTTSettings.get_solo()

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
        json_settings = settings.JSONTelegramMQTTSettings.get_solo()
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
        split_topic_settings = settings.SplitTopicTelegramMQTTSettings.get_solo()
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

    @mock.patch('paho.mqtt.publish.single')
    def test_publish_json_day_totals_overview(self, mqtt_mock):
        json_settings = settings.JSONDayTotalsMQTTSettings.get_solo()
        reading = self._create_dsmrreading()

        # Mapping.
        json_settings.formatting = '''
[mapping]
# DATA = JSON FIELD
electricity1 = aaa
electricity2 = bbb
electricity1_returned = ccc
electricity2_returned = ddd
electricity_merged = eee
electricity_returned_merged = fff
electricity1_cost = ggg
electricity2_cost = hhh
electricity_cost_merged = iii
gas = jjj
gas_cost = kkk
total_cost = lll
'''
        json_settings.save()

        # Disabled by default.
        self.assertFalse(json_settings.enabled)
        self.assertFalse(mqtt_mock.called)
        dsmr_mqtt.services.publish_json_day_totals_overview()
        self.assertFalse(mqtt_mock.called)

        # Now enabled, but no data, so should fail.
        json_settings.enabled = True
        json_settings.save()
        dsmr_mqtt.services.publish_json_day_totals_overview()
        self.assertFalse(mqtt_mock.called)

        # Required for consumption to return any data.
        ElectricityConsumption.objects.bulk_create([
            ElectricityConsumption(
                read_at=reading.timestamp,
                delivered_1=0,
                delivered_2=0,
                returned_1=0,
                returned_2=0,
                currently_delivered=0,
                currently_returned=0,
            ),
            ElectricityConsumption(
                read_at=reading.timestamp + timezone.timedelta(seconds=1),
                delivered_1=12,
                delivered_2=14,
                returned_1=3,
                returned_2=5,
                currently_delivered=0,
                currently_returned=0,
            ),
        ])

        # Should be okay now.
        json_settings.enabled = True
        json_settings.save()
        dsmr_mqtt.services.publish_json_day_totals_overview()
        self.assertTrue(mqtt_mock.called)

        _, _, result = mqtt_mock.mock_calls[0]
        result = json.loads(result['payload'])

        # Without gas or costs.
        self.assertEqual(result['aaa'], '12.000')
        self.assertEqual(result['bbb'], '14.000')
        self.assertEqual(result['ccc'], '3.000')
        self.assertEqual(result['ddd'], '5.000')
        self.assertEqual(result['eee'], '26.000')
        self.assertEqual(result['fff'], '8.000')
        self.assertEqual(result['ggg'], '0.00')
        self.assertEqual(result['hhh'], '0.00')
        self.assertEqual(result['iii'], '0.00')
        self.assertEqual(result['lll'], '0.00')

        # With gas.
        GasConsumption.objects.create(
            read_at=reading.timestamp,
            delivered=1,
            currently_delivered=0,
        )
        GasConsumption.objects.create(
            read_at=reading.timestamp + timezone.timedelta(seconds=1),
            delivered=5.5,
            currently_delivered=0,
        )

        mqtt_mock.reset_mock()
        dsmr_mqtt.services.publish_json_day_totals_overview()

        _, _, result = mqtt_mock.mock_calls[0]
        result = json.loads(result['payload'])

        self.assertEqual(result['jjj'], '4.500')
        self.assertEqual(result['kkk'], '0.00')

        # With costs.
        EnergySupplierPrice.objects.create(
            start=reading.timestamp,
            end=reading.timestamp,
            description='Test',
            electricity_delivered_1_price=3,
            electricity_delivered_2_price=5,
            gas_price=8,
            electricity_returned_1_price=1,
            electricity_returned_2_price=2,
        )
        mqtt_mock.reset_mock()
        dsmr_mqtt.services.publish_json_day_totals_overview()
        '''
        [mapping]
        # DATA = JSON FIELD
        electricity1_cost = ggg
        electricity2_cost = hhh
        electricity_cost_merged = iii
        gas_cost = kkk
        total_cost = lll
        '''
        _, _, result = mqtt_mock.mock_calls[0]
        result = json.loads(result['payload'])

        self.assertEqual(result['ggg'], '33.00')
        self.assertEqual(result['hhh'], '60.00')
        self.assertEqual(result['iii'], '93.00')
        self.assertEqual(result['lll'], '129.00')

        # On error.
        mqtt_mock.side_effect = ValueError('Invalid host.')
        dsmr_mqtt.services.publish_json_day_totals_overview()
