from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_weather.models.settings import WeatherSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = WeatherSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(WeatherSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_track(self):
        self.assertFalse(self.instance.track)

    def test_buienradar_station(self):
        self.assertEqual(self.instance.buienradar_station, 6260)
