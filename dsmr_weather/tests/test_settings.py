from django.test import TestCase

from dsmr_weather.models.settings import WeatherSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = WeatherSettings().get_solo()

    def test_track(self):
        self.assertFalse(self.instance.track)

    def test_buienradar_station(self):
        self.assertEqual(self.instance.buienradar_station, 6260)
