from unittest import mock

from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_mqtt.models.settings import broker, day_totals, telegram, meter_statistics, consumption


class TestBrokerSettings(TestCase):
    def setUp(self):
        self.instance = broker.MQTTBrokerSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(broker.MQTTBrokerSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    @mock.patch('dsmr_mqtt.apps.MqttAppConfig._on_broker_settings_updated_signal')
    def test_signal(self, signal_mock):
        self.assertFalse(broker.MQTTBrokerSettings.objects.filter(restart_required=True).exists())

        self.instance.hostname = 'test'
        self.instance.save()

        self.assertTrue(broker.MQTTBrokerSettings.objects.filter(restart_required=True).exists())


class TestRawTelegramSettings(TestCase):
    def setUp(self):
        self.instance = telegram.RawTelegramMQTTSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(telegram.RawTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestJSONTelegramSettings(TestCase):
    def setUp(self):
        self.instance = telegram.JSONTelegramMQTTSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(telegram.JSONTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestSplitTopicTelegramMQTTSettings(TestCase):
    def setUp(self):
        self.instance = telegram.SplitTopicTelegramMQTTSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(telegram.SplitTopicTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestJSONDayTotalsMQTTSettings(TestCase):
    def setUp(self):
        self.instance = day_totals.JSONDayTotalsMQTTSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(day_totals.JSONDayTotalsMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestSplitTopicDayTotalsMQTTSettings(TestCase):
    def setUp(self):
        self.instance = day_totals.SplitTopicDayTotalsMQTTSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(day_totals.SplitTopicDayTotalsMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestSplitTopicMeterStatisticsMQTTSettings(TestCase):
    def setUp(self):
        self.instance = meter_statistics.SplitTopicMeterStatisticsMQTTSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(meter_statistics.SplitTopicMeterStatisticsMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestJSONGasConsumptionMQTTSettings(TestCase):
    def setUp(self):
        self.instance = consumption.JSONGasConsumptionMQTTSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(consumption.JSONGasConsumptionMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestSplitTopicGasConsumptionMQTTSettings(TestCase):
    def setUp(self):
        self.instance = consumption.SplitTopicGasConsumptionMQTTSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(consumption.SplitTopicGasConsumptionMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))
