from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_influxdb.models import InfluxdbIntegrationSettings
from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_backup.models.settings import BackupSettings, DropboxSettings
from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings
import dsmr_backend.services.backend


class TestBackend(InterceptStdoutMixin, TestCase):
    def test_data_capabilities(self):
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertIn('electricity', capabilities.keys())
        self.assertIn('electricity_returned', capabilities.keys())
        self.assertIn('gas', capabilities.keys())
        self.assertIn('weather', capabilities.keys())
        self.assertIn('any', capabilities.keys())

    def test_empty_capabilities(self):
        """ Capability check for empty database. """
        capabilities = dsmr_backend.services.backend.get_capabilities()

        self.assertFalse(WeatherSettings.get_solo().track)

        self.assertFalse(capabilities['electricity'])
        self.assertFalse(capabilities['electricity_returned'])
        self.assertFalse(capabilities['gas'])
        self.assertFalse(capabilities['multi_phases'])
        self.assertFalse(capabilities['weather'])
        self.assertFalse(capabilities['any'])

        self.assertFalse(dsmr_backend.services.backend.get_capabilities('electricity'))
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('electricity_returned'))
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('gas'))
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('multi_phases'))
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('weather'))
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('any'))

    def test_electricity_capabilities(self):
        """ Capability check for electricity consumption. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
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
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capabilities('electricity'))
        self.assertTrue(capabilities['electricity'])
        self.assertTrue(capabilities['any'])

    def test_multi_phases_capabilities(self):
        """ Capability check for multiple phases. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities['multi_phases'])
        self.assertFalse(capabilities['any'])

        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0,
            currently_returned=0,
            phase_currently_delivered_l1=1,
            phase_currently_returned_l1=2,
        )

        # Should fail.
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('multi_phases'))

        ElectricityConsumption.objects.create(
            read_at=timezone.now() + timezone.timedelta(minutes=1),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0,
            currently_returned=0,
            phase_currently_delivered_l2=1,
            phase_currently_delivered_l3=1,
            phase_currently_returned_l2=2,
            phase_currently_returned_l3=2,
        )
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capabilities('multi_phases'))

        self.assertTrue(capabilities['multi_phases'])
        self.assertTrue(capabilities['any'])

    def test_multi_phases_capabilities_belgium(self):
        """ Capability check for multiple phases, Belgium version which lack some fields. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities['multi_phases'])
        self.assertFalse(capabilities['any'])

        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0,
            currently_returned=0,
            phase_voltage_l2=None,
            phase_voltage_l3=None,
        )

        # Should fail.
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('multi_phases'))

        ElectricityConsumption.objects.create(
            read_at=timezone.now() + timezone.timedelta(minutes=1),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0,
            currently_returned=0,
            phase_voltage_l2=1,
            phase_voltage_l3=2,
        )
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capabilities('multi_phases'))

        self.assertTrue(capabilities['multi_phases'])
        self.assertTrue(capabilities['any'])

    def test_electricity_returned_capabilities(self):
        """ Capability check for electricity returned. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
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
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities['electricity_returned'])

        consumption.currently_returned = 0.001
        consumption.save(update_fields=['currently_returned'])
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capabilities('electricity_returned'))
        self.assertTrue(capabilities['electricity_returned'])
        self.assertTrue(capabilities['any'])

    def test_gas_capabilities(self):
        """ Capability check for gas consumption. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities['gas'])
        self.assertFalse(capabilities['any'])

        GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=0,
            currently_delivered=0,
        )
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capabilities('gas'))
        self.assertTrue(capabilities['gas'])
        self.assertTrue(capabilities['any'])

    def test_weather_capabilities(self):
        """ Capability check for gas consumption. """
        weather_settings = WeatherSettings.get_solo()
        self.assertFalse(weather_settings.track)
        self.assertFalse(TemperatureReading.objects.exists())

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities['weather'])
        self.assertFalse(capabilities['any'])

        # Should not have any affect.
        weather_settings.track = True
        weather_settings.save(update_fields=['track'])
        self.assertTrue(WeatherSettings.get_solo().track)

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities['weather'])

        TemperatureReading.objects.create(read_at=timezone.now(), degrees_celcius=0.0)
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capabilities('weather'))
        self.assertTrue(capabilities['weather'])
        self.assertTrue(capabilities['any'])

    def test_disabled_capabilities(self):
        """ Whether disable capabilities affects the outcome. """
        BackendSettings.get_solo()
        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=1,
            returned_1=2,
            delivered_2=3,
            returned_2=4,
            currently_delivered=5,
            currently_returned=6,
        )
        GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=1,
            currently_delivered=1,
        )

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capabilities('gas'))
        self.assertTrue(capabilities['gas'])
        self.assertTrue(dsmr_backend.services.backend.get_capabilities('electricity_returned'))
        self.assertTrue(capabilities['electricity_returned'])

        # Disable gas.
        BackendSettings.objects.all().update(disable_gas_capability=True)

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('gas'))
        self.assertFalse(capabilities['gas'])

        # Disable return.
        BackendSettings.objects.all().update(disable_electricity_returned_capability=True)

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('electricity_returned'))
        self.assertFalse(capabilities['electricity_returned'])

    @mock.patch('django.core.cache.cache.set')
    @mock.patch('django.core.cache.cache.get')
    def test_capability_caching(self, get_cache_mock, set_cache_mock):
        """ Whether capabilities are cached. """
        get_cache_mock.return_value = None

        self.assertFalse(get_cache_mock.called)
        self.assertFalse(set_cache_mock.called)

        first_capabilities = dsmr_backend.services.backend.get_capabilities()

        self.assertTrue(get_cache_mock.called)
        self.assertTrue(set_cache_mock.called)

        # Now we should retreive from cache.
        set_cache_mock.reset_mock()
        get_cache_mock.return_value = first_capabilities  # Fake caching.

        second_capabilities = dsmr_backend.services.backend.get_capabilities()

        self.assertTrue(get_cache_mock.called)
        self.assertFalse(set_cache_mock.called)
        self.assertEqual(first_capabilities, second_capabilities)

    @mock.patch('django.utils.timezone.now')
    def test_hours_in_day(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 3, 29))
        self.assertEqual(dsmr_backend.services.backend.hours_in_day(day=timezone.now().date()), 23)

        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 7, 1))
        self.assertEqual(dsmr_backend.services.backend.hours_in_day(day=timezone.now().date()), 24)

        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 10, 25))
        self.assertEqual(dsmr_backend.services.backend.hours_in_day(day=timezone.now().date()), 25)


@mock.patch('requests.get')
class TestIslatestVersion(TestCase):
    response_older = [
        {
            "name": "v1.2.0"
        },
        {
            "name": "v1.1.0"
        }
    ]

    response_newer = [
        {
            "name": "v10.99.0"
        },
        {
            "name": "v1.1.0"
        }
    ]

    def test_true(self, get_mock):
        request_mock = mock.MagicMock()
        request_mock.json.return_value = self.response_older
        get_mock.return_value = request_mock

        self.assertTrue(dsmr_backend.services.backend.is_latest_version())

    def test_false(self, get_mock):
        request_mock = mock.MagicMock()
        request_mock.json.return_value = self.response_newer
        get_mock.return_value = request_mock

        self.assertFalse(dsmr_backend.services.backend.is_latest_version())


class TestIsLocalTimestampPassed(TestCase):
    @mock.patch('django.utils.timezone.now')
    def test_true(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1, hour=13, minute=37))

        self.assertTrue(
            dsmr_backend.services.backend.is_timestamp_passed(timestamp=timezone.now() - timezone.timedelta(minutes=1))
        )
        self.assertTrue(
            dsmr_backend.services.backend.is_timestamp_passed(timestamp=timezone.now())
        )

    def test_false(self):
        self.assertFalse(
            dsmr_backend.services.backend.is_timestamp_passed(timestamp=timezone.now() + timezone.timedelta(minutes=1))
        )

    def test_none(self):
        self.assertTrue(dsmr_backend.services.backend.is_timestamp_passed(None))
