from unittest import mock

from django.test import TestCase

from dsmrreader import signals
from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.statistics import TemperatureReading
import dsmr_weather.services


class TestDsmrWeatherServices(TestCase):
    """ Test services. """
    @mock.patch('dsmr_weather.services.read_weather')
    def test_consumption_creation_signal(self, service_mock):
        """ Test incoming signal handling, set in app config. """
        self.assertFalse(service_mock.called)
        signals.gas_consumption_created.send(None, instance=object())
        self.assertTrue(service_mock.called)

    def test_read_weather(self):
        """ Tests whether temperature readings are skipped when tracking is disabled. """
        self.assertFalse(WeatherSettings.get_solo().track)
        self.assertFalse(TemperatureReading.objects.all().exists())
        dsmr_weather.services.read_weather()
        self.assertFalse(TemperatureReading.objects.all().exists())
