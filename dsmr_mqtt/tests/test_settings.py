from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_mqtt.models.settings import MQTTBrokerSettings, RawTelegramMQTTSettings, JSONTelegramMQTTSettings,\
    SplitTopicTelegramMQTTSettings


class TestBrokerSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = MQTTBrokerSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(MQTTBrokerSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestRawTelegramSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = RawTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(RawTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestJSONTelegramSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = JSONTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(JSONTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class SplitTopicTelegramMQTTSettingsSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = SplitTopicTelegramMQTTSettings.get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(SplitTopicTelegramMQTTSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))
