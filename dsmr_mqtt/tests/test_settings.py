from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_mqtt.models.settings import broker, day_totals, telegram


class TestBrokerSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = broker.MQTTBrokerSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(broker.MQTTBrokerSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestRawTelegramSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = telegram.RawTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(telegram.RawTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestJSONTelegramSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = telegram.JSONTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(telegram.JSONTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class SplitTopicTelegramMQTTSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = telegram.SplitTopicTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(telegram.SplitTopicTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class JSONDayTotalsMQTTSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = day_totals.JSONDayTotalsMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(day_totals.JSONDayTotalsMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class SplitTopicDayTotalsMQTTSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = day_totals.SplitTopicDayTotalsMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(day_totals.SplitTopicDayTotalsMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))
