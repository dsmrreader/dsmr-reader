from unittest import mock
from decimal import Decimal
import os

from django.test import TestCase
from django.conf import settings

from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.statistics import TemperatureReading
import dsmr_consumption.signals
import dsmr_weather.services


class TestDsmrWeatherServices(TestCase):
    """ Test services. """
    @mock.patch('dsmr_weather.services.read_weather')
    def test_consumption_creation_signal(self, service_mock):
        """ Test incoming signal handling, set in app config. """
        self.assertFalse(service_mock.called)
        dsmr_consumption.signals.gas_consumption_created.send_robust(None, instance=object())
        self.assertTrue(service_mock.called)

    def test_weather_tracking(self):
        """ Tests whether temperature readings are skipped when tracking is disabled. """
        self.assertFalse(WeatherSettings.get_solo().track)
        self.assertFalse(TemperatureReading.objects.all().exists())
        dsmr_weather.services.read_weather()
        self.assertFalse(TemperatureReading.objects.all().exists())

    @mock.patch('urllib.request.urlopen')
    def test_weather_parsing(self, urlopen_mock):
        """ Tests whether temperature readings are skipped when tracking is disabled. """
        weather_settings = WeatherSettings.get_solo()
        weather_settings.track = True
        weather_settings.save()

        # Fake URL opener and its http response object used for reading data.
        http_response_mock = mock.MagicMock()

        test_data_file = os.path.join(
            settings.BASE_DIR, '..', 'dsmr_weather', 'tests', 'data', 'api.buienradar.nl.xml'
        )

        with open(test_data_file, 'r') as data:
            # Http response is in bytes, so make sure to equalize it.
            http_response_mock.read.return_value = bytes(data.read(), encoding='utf-8')

        urlopen_mock.return_value = http_response_mock

        self.assertFalse(TemperatureReading.objects.all().exists())
        dsmr_weather.services.read_weather()
        self.assertTrue(TemperatureReading.objects.all().exists())

        # Test data snapshot read 4.8 degrees @ De Bilt.
        reading = TemperatureReading.objects.get()
        self.assertEqual(weather_settings.buienradar_station, 6260)
        self.assertEqual(reading.degrees_celcius, Decimal('4.8'))
