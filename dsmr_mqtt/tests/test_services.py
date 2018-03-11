from unittest import mock
import json

from django.test import TestCase
from django.utils import timezone

from dsmr_mqtt.models.settings import broker, day_totals, telegram
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


class TestBroker(TestServices):
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


class TestTelegramAndReading(TestServices):
    @mock.patch('dsmr_mqtt.services.publish_raw_dsmr_telegram')
    def test_raw_telegram_signal(self, service_mock):
        self.assertFalse(service_mock.called)
        dsmr_datalogger.signals.raw_telegram.send_robust(sender=None, data='test')
        self.assertTrue(service_mock.called)

    @mock.patch('dsmr_mqtt.services.publish_json_dsmr_reading')
    @mock.patch('dsmr_mqtt.services.publish_split_topic_dsmr_reading')
    @mock.patch('dsmr_mqtt.services.publish_day_totals')
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
    def test_publish_json_dsmr_reading(self, mqtt_mock):
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


class TestDaytotals(TestServices):
    def setUp(self):
        self.json_settings = day_totals.JSONDayTotalsMQTTSettings.get_solo()
        self.split_topic_settings = day_totals.SplitTopicDayTotalsMQTTSettings.get_solo()
        self.reading = self._create_dsmrreading()

        # Mapping.
        self.json_settings.formatting = '''
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
energy_supplier_price_electricity_delivered_1 = mmm
energy_supplier_price_electricity_delivered_2 = nnn
energy_supplier_price_electricity_returned_1 = ooo
energy_supplier_price_electricity_returned_2 = ppp
energy_supplier_price_gas = qqq
'''
        self.json_settings.save()

        self.split_topic_settings.formatting = '''
[mapping]
# DATA = JSON FIELD
electricity1 = dsmr/aaa
electricity2 = dsmr/bbb
electricity1_returned = dsmr/ccc
electricity2_returned = dsmr/ddd
electricity_merged = dsmr/eee
electricity_returned_merged = dsmr/fff
electricity1_cost = dsmr/ggg
electricity2_cost = dsmr/hhh
electricity_cost_merged = dsmr/iii

# Gas (if any)
gas = dsmr/jjj
gas_cost = dsmr/kkk
total_cost = dsmr/lll

# Your energy supplier prices (if set)
energy_supplier_price_electricity_delivered_1 = dsmr/mmm
energy_supplier_price_electricity_delivered_2 = dsmr/nnn
energy_supplier_price_electricity_returned_1 = dsmr/ooo
energy_supplier_price_electricity_returned_2 = dsmr/ppp
energy_supplier_price_gas = dsmr/qqq
'''
        self.split_topic_settings.save()

    @mock.patch('paho.mqtt.publish.multiple')
    def test_disabled(self, mqtt_mock):
        self.assertFalse(self.json_settings.enabled)
        self.assertFalse(self.split_topic_settings.enabled)
        self.assertFalse(mqtt_mock.called)

        dsmr_mqtt.services.publish_day_totals()
        self.assertFalse(mqtt_mock.called)

    @mock.patch('paho.mqtt.publish.multiple')
    def test_no_data(self, mqtt_mock):
        self.json_settings.enabled = True
        self.json_settings.save()

        self.assertFalse(mqtt_mock.called)
        dsmr_mqtt.services.publish_day_totals()
        self.assertFalse(mqtt_mock.called)

    @mock.patch('paho.mqtt.publish.multiple')
    def test_json(self, mqtt_mock):
        # Required for consumption to return any data.
        ElectricityConsumption.objects.bulk_create([
            ElectricityConsumption(
                read_at=self.reading.timestamp,
                delivered_1=0,
                delivered_2=0,
                returned_1=0,
                returned_2=0,
                currently_delivered=0,
                currently_returned=0,
            ),
            ElectricityConsumption(
                read_at=self.reading.timestamp + timezone.timedelta(seconds=1),
                delivered_1=12,
                delivered_2=14,
                returned_1=3,
                returned_2=5,
                currently_delivered=0,
                currently_returned=0,
            ),
        ])

        # Should be okay now.
        self.json_settings.enabled = True
        self.json_settings.save()
        dsmr_mqtt.services.publish_day_totals()
        self.assertTrue(mqtt_mock.called)

        _, _, result = mqtt_mock.mock_calls[0]
        result = json.loads(result['msgs'][0]['payload'])

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
            read_at=self.reading.timestamp,
            delivered=1,
            currently_delivered=0,
        )
        GasConsumption.objects.create(
            read_at=self.reading.timestamp + timezone.timedelta(seconds=1),
            delivered=5.5,
            currently_delivered=0,
        )

        mqtt_mock.reset_mock()
        dsmr_mqtt.services.publish_day_totals()

        _, _, result = mqtt_mock.mock_calls[0]
        result = json.loads(result['msgs'][0]['payload'])

        self.assertEqual(result['jjj'], '4.500')
        self.assertEqual(result['kkk'], '0.00')

        # With costs.
        EnergySupplierPrice.objects.create(
            start=self.reading.timestamp,
            end=self.reading.timestamp,
            description='Test',
            electricity_delivered_1_price=3,
            electricity_delivered_2_price=5,
            electricity_returned_1_price=1,
            electricity_returned_2_price=2,
            gas_price=8,
        )
        mqtt_mock.reset_mock()
        dsmr_mqtt.services.publish_day_totals()

        _, _, result = mqtt_mock.mock_calls[0]
        result = json.loads(result['msgs'][0]['payload'])

        self.assertEqual(result['ggg'], '33.00')
        self.assertEqual(result['hhh'], '60.00')
        self.assertEqual(result['iii'], '93.00')
        self.assertEqual(result['lll'], '129.00')

        self.assertEqual(result['mmm'], '3.00000')
        self.assertEqual(result['nnn'], '5.00000')
        self.assertEqual(result['ooo'], '1.00000')
        self.assertEqual(result['ppp'], '2.00000')
        self.assertEqual(result['qqq'], '8.00000')

    @mock.patch('paho.mqtt.publish.multiple')
    def test_split_topic(self, mqtt_mock):
        # Required for consumption to return any data.
        ElectricityConsumption.objects.bulk_create([
            ElectricityConsumption(
                read_at=self.reading.timestamp,
                delivered_1=0,
                delivered_2=0,
                returned_1=0,
                returned_2=0,
                currently_delivered=0,
                currently_returned=0,
            ),
            ElectricityConsumption(
                read_at=self.reading.timestamp + timezone.timedelta(seconds=1),
                delivered_1=12,
                delivered_2=14,
                returned_1=3,
                returned_2=5,
                currently_delivered=0,
                currently_returned=0,
            ),
        ])
        GasConsumption.objects.create(
            read_at=self.reading.timestamp,
            delivered=1,
            currently_delivered=0,
        )
        GasConsumption.objects.create(
            read_at=self.reading.timestamp + timezone.timedelta(seconds=1),
            delivered=5.5,
            currently_delivered=0,
        )
        EnergySupplierPrice.objects.create(
            start=self.reading.timestamp,
            end=self.reading.timestamp,
            description='Test',
            electricity_delivered_1_price=3,
            electricity_delivered_2_price=5,
            electricity_returned_1_price=1,
            electricity_returned_2_price=2,
            gas_price=8,
        )

        # Should be okay now.
        self.split_topic_settings.enabled = True
        self.split_topic_settings.save()
        dsmr_mqtt.services.publish_day_totals()
        self.assertTrue(mqtt_mock.called)

        _, _, kwargs = mqtt_mock.mock_calls[0]
        mqtt_messages = kwargs['msgs']

        # Without gas or costs.
        self.assertIn({'payload': 12.0, 'topic': 'dsmr/aaa'}, mqtt_messages)
        self.assertIn({'payload': 14.0, 'topic': 'dsmr/bbb'}, mqtt_messages)
        self.assertIn({'payload': 3.0, 'topic': 'dsmr/ccc'}, mqtt_messages)
        self.assertIn({'payload': 5.0, 'topic': 'dsmr/ddd'}, mqtt_messages)
        self.assertIn({'payload': 26.0, 'topic': 'dsmr/eee'}, mqtt_messages)
        self.assertIn({'payload': 8.0, 'topic': 'dsmr/fff'}, mqtt_messages)

        self.assertIn({'payload': 4.5, 'topic': 'dsmr/jjj'}, mqtt_messages)
        self.assertIn({'payload': 36.0, 'topic': 'dsmr/kkk'}, mqtt_messages)

        self.assertIn({'payload': 33.0, 'topic': 'dsmr/ggg'}, mqtt_messages)
        self.assertIn({'payload': 60.0, 'topic': 'dsmr/hhh'}, mqtt_messages)
        self.assertIn({'payload': 93.0, 'topic': 'dsmr/iii'}, mqtt_messages)
        self.assertIn({'payload': 129.0, 'topic': 'dsmr/lll'}, mqtt_messages)

        self.assertIn({'payload': 3.0, 'topic': 'dsmr/mmm'}, mqtt_messages)
        self.assertIn({'payload': 5.0, 'topic': 'dsmr/nnn'}, mqtt_messages)
        self.assertIn({'payload': 1.0, 'topic': 'dsmr/ooo'}, mqtt_messages)
        self.assertIn({'payload': 2.0, 'topic': 'dsmr/ppp'}, mqtt_messages)
        self.assertIn({'payload': 8.0, 'topic': 'dsmr/qqq'}, mqtt_messages)

        # On error.
        mqtt_mock.side_effect = ValueError('Invalid host.')
        dsmr_mqtt.services.publish_day_totals()
