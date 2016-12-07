from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
import dsmr_backend.services


class TestServices(InterceptStdoutMixin, TestCase):
    support_gas_readings = None

    def test_data_capabilities(self):
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertIn('electricity', capabilities.keys())
        self.assertIn('electricity_returned', capabilities.keys())
        self.assertIn('gas', capabilities.keys())
        self.assertIn('weather', capabilities.keys())
        self.assertIn('any', capabilities.keys())

    def test_empty_capabilities(self):
        """ Capability check for empty database. """
        capabilities = dsmr_backend.services.get_capabilities()

        self.assertFalse(WeatherSettings.get_solo().track)

        self.assertFalse(capabilities['electricity'])
        self.assertFalse(capabilities['electricity_returned'])
        self.assertFalse(capabilities['gas'])
        self.assertFalse(capabilities['weather'])
        self.assertFalse(capabilities['any'])

        self.assertFalse(dsmr_backend.services.get_capabilities('electricity'))
        self.assertFalse(dsmr_backend.services.get_capabilities('electricity_returned'))
        self.assertFalse(dsmr_backend.services.get_capabilities('gas'))
        self.assertFalse(dsmr_backend.services.get_capabilities('weather'))
        self.assertFalse(dsmr_backend.services.get_capabilities('any'))

    def test_electricity_capabilities(self):
        """ Capability check for electricity consumption. """
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertFalse(capabilities['electricity'])
        self.assertFalse(capabilities['any'])

        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0,
            currently_returned=0,
        )
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertTrue(dsmr_backend.services.get_capabilities('electricity'))
        self.assertTrue(capabilities['electricity'])
        self.assertTrue(capabilities['any'])

    def test_electricity_returned_capabilities(self):
        """ Capability check for electricity returned. """
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertFalse(capabilities['electricity_returned'])
        self.assertFalse(capabilities['any'])

        # Should not have any affect.
        consumption = ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0,
            currently_returned=0,
        )
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertFalse(capabilities['electricity_returned'])

        consumption.currently_returned = 0.001
        consumption.save(update_fields=['currently_returned'])
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertTrue(dsmr_backend.services.get_capabilities('electricity_returned'))
        self.assertTrue(capabilities['electricity_returned'])
        self.assertTrue(capabilities['any'])

    def test_gas_capabilities(self):
        """ Capability check for gas consumption. """
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertFalse(capabilities['gas'])
        self.assertFalse(capabilities['any'])

        GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=0,
            currently_delivered=0,
        )
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertTrue(dsmr_backend.services.get_capabilities('gas'))
        self.assertTrue(capabilities['gas'])
        self.assertTrue(capabilities['any'])

    def test_weather_capabilities(self):
        """ Capability check for gas consumption. """
        weather_settings = WeatherSettings.get_solo()
        self.assertFalse(weather_settings.track)
        self.assertFalse(TemperatureReading.objects.exists())

        capabilities = dsmr_backend.services.get_capabilities()
        self.assertFalse(capabilities['weather'])
        self.assertFalse(capabilities['any'])

        # Should not have any affect.
        weather_settings.track = True
        weather_settings.save(update_fields=['track'])
        self.assertTrue(WeatherSettings.get_solo().track)

        capabilities = dsmr_backend.services.get_capabilities()
        self.assertFalse(capabilities['weather'])

        TemperatureReading.objects.create(read_at=timezone.now(), degrees_celcius=0.0)
        capabilities = dsmr_backend.services.get_capabilities()
        self.assertTrue(dsmr_backend.services.get_capabilities('weather'))
        self.assertTrue(capabilities['weather'])
        self.assertTrue(capabilities['any'])


@mock.patch('requests.get')
class TestIslatestVersion(TestCase):
    response_older = b"from django.utils.version import get_version\n" \
        b"VERSION = (1, 2, 0, 'final', 0)\n" \
        b"__version__ = get_version(VERSION)\n"

    response_newer = b"from django.utils.version import get_version\n" \
        b"VERSION = (1, 5, 1, 'final', 0)\n" \
        b"__version__ = get_version(VERSION)\n"

    def test_true(self, request_mock):
        response_mock = mock.MagicMock(content=self.response_older)
        request_mock.return_value = response_mock

        self.assertTrue(dsmr_backend.services.is_latest_version())

    def test_false(self, request_mock):
        response_mock = mock.MagicMock(content=self.response_newer)
        request_mock.return_value = response_mock

        self.assertFalse(dsmr_backend.services.is_latest_version())
