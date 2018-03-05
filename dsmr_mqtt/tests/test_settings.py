from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_mqtt.models import settings


class TestBrokerSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = settings.MQTTBrokerSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(settings.MQTTBrokerSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestRawTelegramSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = settings.RawTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(settings.RawTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestJSONTelegramSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = settings.JSONTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(settings.JSONTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class SplitTopicTelegramMQTTSettingsSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = settings.SplitTopicTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(settings.SplitTopicTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class JSONDayTotalsMQTTSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = settings.JSONDayTotalsMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(settings.JSONDayTotalsMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))
