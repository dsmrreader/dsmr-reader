from unittest import mock

from django.test.utils import override_settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_backup.models.settings import BackupSettings, DropboxSettings
from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings
import dsmr_backend.services.backend


class TestServices(InterceptStdoutMixin, TestCase):
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

    @override_settings(DSMRREADER_DISABLED_CAPABILITIES=['electricity'])
    def test_disabled_capabilities(self):
        """ Whether DSMRREADER_DISABLED_CAPABILITIES affects the outcome. """
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
        self.assertFalse(dsmr_backend.services.backend.get_capabilities('electricity'))
        self.assertFalse(capabilities['electricity'])

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
    def test_status_info(self, now_mock):
        """ Application status info dict. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1))

        BackupSettings.get_solo()
        BackupSettings.objects.update(daily_backup=False)
        tools_status = dsmr_backend.services.backend.status_info()['tools']

        # Tools should be asserted, other content is tested in dsmr_frontend.
        self.assertFalse(tools_status['backup']['enabled'])
        self.assertFalse(tools_status['dropbox']['enabled'])
        self.assertFalse(tools_status['pvoutput']['enabled'])
        self.assertFalse(tools_status['mindergas']['enabled'])
        self.assertIsNone(tools_status['backup']['latest_backup'])
        self.assertIsNone(tools_status['dropbox']['latest_sync'])
        self.assertIsNone(tools_status['pvoutput']['latest_sync'])
        self.assertIsNone(tools_status['mindergas']['latest_sync'])

        # Now when enabled.
        BackupSettings.objects.update(daily_backup=True, latest_backup=timezone.now())
        DropboxSettings.objects.update(access_token='xxx', latest_sync=timezone.now())
        MinderGasSettings.objects.update(export=True, latest_sync=timezone.now())
        PVOutputAddStatusSettings.objects.update(export=True, latest_sync=timezone.now())

        tools_status = dsmr_backend.services.backend.status_info()['tools']

        self.assertTrue(tools_status['backup']['enabled'])
        self.assertTrue(tools_status['dropbox']['enabled'])
        self.assertTrue(tools_status['pvoutput']['enabled'])
        self.assertTrue(tools_status['mindergas']['enabled'])
        self.assertEqual(tools_status['backup']['latest_backup'], timezone.now())
        self.assertEqual(tools_status['dropbox']['latest_sync'], timezone.now())
        self.assertEqual(tools_status['pvoutput']['latest_sync'], timezone.now())
        self.assertEqual(tools_status['mindergas']['latest_sync'], timezone.now())


@mock.patch('requests.get')
class TestIslatestVersion(TestCase):
    response_older = b"from django.utils.version import get_version\n" \
        b"VERSION = (1, 2, 0, 'final', 0)\n" \
        b"__version__ = get_version(VERSION)\n"

    response_newer = b"from django.utils.version import get_version\n" \
        b"VERSION = (2, 99, 0, 'final', 0)\n" \
        b"__version__ = get_version(VERSION)\n"

    def test_true(self, request_mock):
        response_mock = mock.MagicMock(content=self.response_older)
        request_mock.return_value = response_mock

        self.assertTrue(dsmr_backend.services.backend.is_latest_version())

    def test_false(self, request_mock):
        response_mock = mock.MagicMock(content=self.response_newer)
        request_mock.return_value = response_mock

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
