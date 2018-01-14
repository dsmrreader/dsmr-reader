from unittest import mock
from decimal import Decimal
import os

from django.test import TestCase
from django.conf import settings
from django.utils import timezone

from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.reading import TemperatureReading
import dsmr_weather.services


class TestDsmrWeatherServices(TestCase):
    """ Test services. """
    @mock.patch('urllib.request.urlopen')
    @mock.patch('django.utils.timezone.now')
    def test_next_sync(self, now_mock, urlopen_mock):
        """ Test next_sync setting. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))

        # We just want to see whether it's called.
        urlopen_mock.side_effect = AssertionError('MOCK')

        weather_settings = WeatherSettings.get_solo()
        weather_settings.track = True
        weather_settings.save()

        self.assertTrue(weather_settings.track)
        self.assertIsNone(weather_settings.next_sync)
        self.assertFalse(urlopen_mock.called)
        self.assertFalse(TemperatureReading.objects.all().exists())

        # Any errors fetching the data should result in a retry later.
        dsmr_weather.services.read_weather()

        weather_settings = WeatherSettings.get_solo()
        self.assertFalse(TemperatureReading.objects.all().exists())
        self.assertEqual(weather_settings.next_sync, timezone.now() + timezone.timedelta(minutes=5))

        # The default next_sync setting should allow initial sync.
        self.assertTrue(urlopen_mock.called)

        # Now disallow.
        weather_settings.next_sync = timezone.now() + timezone.timedelta(minutes=15)
        weather_settings.save()

        urlopen_mock.reset_mock()
        self.assertFalse(urlopen_mock.called)

        dsmr_weather.services.read_weather()

        # Should be skipped now.
        self.assertFalse(urlopen_mock.called)

    def test_weather_tracking(self):
        """ Tests whether temperature readings are skipped when tracking is disabled. """
        self.assertFalse(WeatherSettings.get_solo().track)
        self.assertFalse(TemperatureReading.objects.all().exists())
        dsmr_weather.services.read_weather()
        self.assertFalse(TemperatureReading.objects.all().exists())

    @mock.patch('urllib.request.urlopen')
    @mock.patch('django.utils.timezone.now')
    def test_weather_parsing(self, now_mock, urlopen_mock):
        """ Tests whether temperature readings are skipped when tracking is disabled. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        weather_settings = WeatherSettings.get_solo()
        weather_settings.track = True
        weather_settings.next_sync = timezone.now() - timezone.timedelta(minutes=15)
        weather_settings.save()
        weather_settings.refresh_from_db()

        self.assertGreater(timezone.now(), weather_settings.next_sync)

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

        # Make sure that the next_sync is pushed forward as well.
        weather_settings = WeatherSettings.get_solo()
        self.assertEqual(weather_settings.next_sync, timezone.now() + timezone.timedelta(hours=1))

    @mock.patch('urllib.request.urlopen')
    @mock.patch('django.utils.timezone.now')
    def test_weather_parsing_error(self, now_mock, urlopen_mock):
        """ Tests whether temperature readings are skipped when tracking is disabled. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        weather_settings = WeatherSettings.get_solo()
        weather_settings.track = True
        weather_settings.next_sync = timezone.now() - timezone.timedelta(minutes=15)
        weather_settings.save()
        weather_settings.refresh_from_db()

        self.assertGreater(timezone.now(), weather_settings.next_sync)

        # Fake URL opener and its http response object used for reading data.
        http_response_mock = mock.MagicMock()

        test_data_file = os.path.join(
            settings.BASE_DIR, '..', 'dsmr_weather', 'tests', 'data', 'invalid-api.buienradar.nl.xml'
        )

        with open(test_data_file, 'r') as data:
            # Http response is in bytes, so make sure to equalize it.
            http_response_mock.read.return_value = bytes(data.read(), encoding='utf-8')

        urlopen_mock.return_value = http_response_mock

        self.assertFalse(TemperatureReading.objects.all().exists())
        dsmr_weather.services.read_weather()
        self.assertFalse(TemperatureReading.objects.all().exists())

        # Make sure that the next_sync is pushed forward as well.
        weather_settings = WeatherSettings.get_solo()
        self.assertEqual(weather_settings.next_sync, timezone.now() + timezone.timedelta(minutes=5))
