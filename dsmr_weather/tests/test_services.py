from unittest import mock
from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.reading import TemperatureReading
import dsmr_weather.services


class TestDsmrWeatherServices(TestCase):
    schedule_process = None

    def setUp(self):
        WeatherSettings.get_solo()
        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_WEATHER_UPDATE)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2017, 1, 1)))

    @mock.patch('dsmr_weather.services.get_temperature_from_api')
    @mock.patch('django.utils.timezone.now')
    def test_exception_handling(self, now_mock, get_temperature_from_api_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        get_temperature_from_api_mock.side_effect = AssertionError('TEST')  # Simulate any exception.

        dsmr_weather.services.run(self.schedule_process)

        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=1))

    @mock.patch('requests.get')
    @mock.patch('django.utils.timezone.now')
    def test_okay(self, now_mock, requests_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))

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
        dsmr_weather.services.run(self.schedule_process)

        self.assertTrue(TemperatureReading.objects.exists())
        self.assertEqual(TemperatureReading.objects.get().degrees_celcius, Decimal('123.4'))

        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=1))

    @mock.patch('requests.get')
    @mock.patch('django.utils.timezone.now')
    def test_fail_http_connection(self, now_mock, requests_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        requests_mock.side_effect = IOError('Failed to connect')  # Any error is fine.

        with self.assertRaises(RuntimeError):
            dsmr_weather.services.get_temperature_from_api()

    @mock.patch('requests.get')
    @mock.patch('django.utils.timezone.now')
    def test_fail_http_response(self, now_mock, requests_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
        response_mock = mock.MagicMock()
        type(response_mock).status_code = mock.PropertyMock(return_value=500)
        requests_mock.return_value = response_mock

        with self.assertRaises(RuntimeError):
            dsmr_weather.services.get_temperature_from_api()

    @mock.patch('requests.get')
    @mock.patch('django.utils.timezone.now')
    def test_fail_station(self, now_mock, requests_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))
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

        with self.assertRaises(RuntimeError):
            dsmr_weather.services.get_temperature_from_api()
