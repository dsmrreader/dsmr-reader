from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
import dsmr_frontend.services


class TestServices(CallCommandStdoutMixin, TestCase):
    support_gas_readings = None

    def test_data_capabilities(self):
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertIn('electricity', capabilities.keys())
        self.assertIn('electricity_returned', capabilities.keys())
        self.assertIn('gas', capabilities.keys())
        self.assertIn('weather', capabilities.keys())

    def test_empty_capabilities(self):
        """ Capability check for empty database. """
        capabilities = dsmr_frontend.services.get_data_capabilities()

        self.assertFalse(WeatherSettings.get_solo().track)

        self.assertFalse(capabilities['electricity'])
        self.assertFalse(capabilities['electricity_returned'])
        self.assertFalse(capabilities['gas'])
        self.assertFalse(capabilities['weather'])

    def test_electricity_capabilities(self):
        """ Capability check for electricity consumption. """
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertFalse(capabilities['electricity'])

        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0,
            currently_returned=0,
        )
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertTrue(capabilities['electricity'])

    def test_electricity_returned_capabilities(self):
        """ Capability check for electricity returned. """
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertFalse(capabilities['electricity_returned'])

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
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertFalse(capabilities['electricity_returned'])

        consumption.currently_returned = 0.001
        consumption.save(update_fields=['currently_returned'])
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertTrue(capabilities['electricity_returned'])

    def test_gas_capabilities(self):
        """ Capability check for gas consumption. """
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertFalse(capabilities['gas'])

        GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=0,
            currently_delivered=0,
        )
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertTrue(capabilities['gas'])

    def test_weather_capabilities(self):
        """ Capability check for gas consumption. """
        weather_settings = WeatherSettings.get_solo()
        self.assertFalse(weather_settings.track)
        self.assertFalse(TemperatureReading.objects.exists())

        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertFalse(capabilities['weather'])

        # Should not have any affect.
        weather_settings.track = True
        weather_settings.save(update_fields=['track'])
        self.assertTrue(WeatherSettings.get_solo().track)

        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertFalse(capabilities['weather'])

        TemperatureReading.objects.create(read_at=timezone.now(), degrees_celcius=0.0)
        capabilities = dsmr_frontend.services.get_data_capabilities()
        self.assertTrue(capabilities['weather'])
