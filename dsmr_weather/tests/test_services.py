from unittest import mock
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.reading import TemperatureReading
import dsmr_weather.services


class TestDsmrWeatherServices(TestCase):
    def setUp(self):
        WeatherSettings.get_solo()

    @mock.patch('dsmr_weather.services.get_temperature_from_api')
    @mock.patch('django.utils.timezone.now')
    def test_should_update(self, now_mock, get_temperature_from_api_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))

        # Disabled.
        WeatherSettings.objects.all().update(track=False)
        dsmr_weather.services.read_weather()
        self.assertFalse(get_temperature_from_api_mock.called)

        # Postpone.
        WeatherSettings.objects.all().update(track=True, next_sync=timezone.now() + timezone.timedelta(minutes=5))
        dsmr_weather.services.read_weather()
        self.assertFalse(get_temperature_from_api_mock.called)

        # Allow.
        WeatherSettings.objects.all().update(next_sync=timezone.now())
        dsmr_weather.services.read_weather()
        self.assertTrue(get_temperature_from_api_mock.called)

    @mock.patch('dsmr_frontend.services.display_dashboard_message')
    @mock.patch('dsmr_weather.services.get_temperature_from_api')
    @mock.patch('django.utils.timezone.now')
    def test_exception_handling(self, now_mock, get_temperature_from_api_mock, display_dashboard_message_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        get_temperature_from_api_mock.side_effect = EnvironmentError('TEST')  # Simulate any exception.

        WeatherSettings.objects.all().update(track=True, next_sync=timezone.now())

        dsmr_weather.services.read_weather()
        self.assertTrue(display_dashboard_message_mock.called)
        self.assertEqual(WeatherSettings.get_solo().next_sync, timezone.now() + timezone.timedelta(minutes=5))

    @mock.patch('requests.get')
    @mock.patch('django.utils.timezone.now')
    def test_okay(self, now_mock, requests_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        WeatherSettings.objects.all().update(track=True, next_sync=timezone.now() - timezone.timedelta(minutes=15))

        response_mock = mock.MagicMock()
        response_mock.json.return_value = {
            'actual': {
                'stationmeasurements': [{
                    'stationid': WeatherSettings.get_solo().buienradar_station,
                    'groundtemperature': 123.4,
                }]
            }
        }
        type(response_mock).status_code = mock.PropertyMock(return_value=200)
        requests_mock.return_value = response_mock

        self.assertFalse(TemperatureReading.objects.exists())
        dsmr_weather.services.get_temperature_from_api()

        self.assertTrue(TemperatureReading.objects.exists())
        self.assertEqual(TemperatureReading.objects.get().degrees_celcius, Decimal('123.4'))

        # Make sure that the next_sync is pushed forward as well.
        weather_settings = WeatherSettings.get_solo()
        self.assertEqual(weather_settings.next_sync, timezone.now() + timezone.timedelta(hours=1))

    @mock.patch('requests.get')
    @mock.patch('django.utils.timezone.now')
    def test_fail_http(self, now_mock, requests_mock):
        """ Test failing request. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        WeatherSettings.objects.all().update(track=True, next_sync=timezone.now() - timezone.timedelta(minutes=15))

        response_mock = mock.MagicMock()
        type(response_mock).status_code = mock.PropertyMock(return_value=500)
        requests_mock.return_value = response_mock

        with self.assertRaises(EnvironmentError):
            dsmr_weather.services.get_temperature_from_api()

    @mock.patch('requests.get')
    @mock.patch('django.utils.timezone.now')
    def test_fail_station(self, now_mock, requests_mock):
        """ Test unable to find station ID. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        WeatherSettings.objects.all().update(track=True, next_sync=timezone.now() - timezone.timedelta(minutes=15))

        response_mock = mock.MagicMock()
        response_mock.json.return_value = {
            'actual': {
                'stationmeasurements': [{
                    'stationid': 0000,
                    'groundtemperature': 123,
                }]
            }
        }
        type(response_mock).status_code = mock.PropertyMock(return_value=200)
        requests_mock.return_value = response_mock

        with self.assertRaises(EnvironmentError):
            dsmr_weather.services.get_temperature_from_api()
