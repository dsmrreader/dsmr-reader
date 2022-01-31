import importlib
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.dto import MonitoringStatusIssue, Capability
from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmrreader.config import django_overrides
from dsmrreader.config import defaults as settings_used
import dsmr_backend.services.backend


class TestBackend(InterceptCommandStdoutMixin, TestCase):
    def test_undefined_capability(self):
        capabilities = dsmr_backend.services.backend.get_capabilities()
        with self.assertRaises(KeyError):
            _ = capabilities['dummy']

    def test_data_capabilities(self):
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(Capability.ELECTRICITY in capabilities)
        self.assertFalse(Capability.ELECTRICITY_RETURNED in capabilities)
        self.assertFalse(Capability.GAS in capabilities)
        self.assertFalse(Capability.MULTI_PHASES in capabilities)
        self.assertFalse(Capability.WEATHER in capabilities)
        self.assertFalse(Capability.COSTS in capabilities)
        self.assertFalse(Capability.ANY in capabilities)

    def test_empty_capabilities(self):
        """ Capability check for empty database. """
        capabilities = dsmr_backend.services.backend.get_capabilities()

        self.assertFalse(WeatherSettings.get_solo().track)

        self.assertFalse(capabilities[Capability.ELECTRICITY])
        self.assertFalse(capabilities[Capability.ELECTRICITY_RETURNED])
        self.assertFalse(capabilities[Capability.GAS])
        self.assertFalse(capabilities[Capability.MULTI_PHASES])
        self.assertFalse(capabilities[Capability.WEATHER])
        self.assertFalse(capabilities[Capability.POWER_CURRENT])
        self.assertFalse(capabilities[Capability.COSTS])
        self.assertFalse(capabilities[Capability.ANY])

        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.ELECTRICITY))
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.ELECTRICITY_RETURNED))
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.GAS))
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.MULTI_PHASES))
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.WEATHER))
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.POWER_CURRENT))
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.COSTS))
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.ANY))

    def test_electricity_capabilities(self):
        """ Capability check for electricity consumption. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities[Capability.ELECTRICITY])
        self.assertFalse(capabilities[Capability.ANY])

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
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.ELECTRICITY))
        self.assertTrue(capabilities[Capability.ELECTRICITY])
        self.assertTrue(capabilities[Capability.ANY])

    def test_multi_phases_capabilities(self):
        """ Capability check for multiple phases. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities[Capability.MULTI_PHASES])
        self.assertFalse(capabilities[Capability.ANY])

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
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.MULTI_PHASES))

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
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.MULTI_PHASES))

        self.assertTrue(capabilities[Capability.MULTI_PHASES])
        self.assertTrue(capabilities[Capability.ANY])

    def test_multi_phases_capabilities_belgium(self):
        """ Capability check for multiple phases, Belgium version which lack some fields. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities[Capability.MULTI_PHASES])
        self.assertFalse(capabilities[Capability.ANY])

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
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.MULTI_PHASES))

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
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.MULTI_PHASES))

        self.assertTrue(capabilities[Capability.MULTI_PHASES])
        self.assertTrue(capabilities[Capability.ANY])

    def test_electricity_returned_capabilities(self):
        """ Capability check for electricity returned. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities[Capability.ELECTRICITY_RETURNED])
        self.assertFalse(capabilities[Capability.ANY])

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
        self.assertFalse(capabilities[Capability.ELECTRICITY_RETURNED])

        consumption.currently_returned = 0.001
        consumption.save(update_fields=['currently_returned'])
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.ELECTRICITY_RETURNED))
        self.assertTrue(capabilities[Capability.ELECTRICITY_RETURNED])
        self.assertTrue(capabilities[Capability.ANY])

    def test_gas_capabilities(self):
        """ Capability check for gas consumption. """
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities[Capability.GAS])
        self.assertFalse(capabilities[Capability.ANY])

        GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=0,
            currently_delivered=0,
        )
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.GAS))
        self.assertTrue(capabilities[Capability.GAS])
        self.assertTrue(capabilities[Capability.ANY])

    def test_weather_capabilities(self):
        """ Capability check for gas consumption. """
        weather_settings = WeatherSettings.get_solo()
        self.assertFalse(weather_settings.track)
        self.assertFalse(TemperatureReading.objects.exists())

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities[Capability.WEATHER])
        self.assertFalse(capabilities[Capability.ANY])

        # Should not have any affect.
        weather_settings.track = True
        weather_settings.save(update_fields=['track'])
        self.assertTrue(WeatherSettings.get_solo().track)

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities[Capability.WEATHER])

        TemperatureReading.objects.create(read_at=timezone.now(), degrees_celcius=0.0)
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.WEATHER))
        self.assertTrue(capabilities[Capability.WEATHER])
        self.assertTrue(capabilities[Capability.ANY])

    def test_costs_capabilities(self):
        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(capabilities[Capability.COSTS])
        self.assertFalse(capabilities[Capability.ANY])

        EnergySupplierPrice.objects.create(
            start=timezone.now().date(),
            end=(timezone.now() + timezone.timedelta(hours=24)).date(),
            electricity_delivered_1_price=0.010,
            electricity_delivered_2_price=0.020,
        )

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.COSTS))
        self.assertTrue(capabilities[Capability.COSTS])
        self.assertTrue(capabilities[Capability.ANY])

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
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.GAS))
        self.assertTrue(capabilities[Capability.GAS])
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.ELECTRICITY_RETURNED))
        self.assertTrue(capabilities[Capability.ELECTRICITY_RETURNED])

        # Disable gas.
        BackendSettings.objects.all().update(disable_gas_capability=True)

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.GAS))
        self.assertFalse(capabilities[Capability.GAS])

        # Disable return.
        BackendSettings.objects.all().update(disable_electricity_returned_capability=True)

        capabilities = dsmr_backend.services.backend.get_capabilities()
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.ELECTRICITY_RETURNED))
        self.assertFalse(capabilities[Capability.ELECTRICITY_RETURNED])

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

    @mock.patch('dsmr_backend.signals.request_status.send_robust')
    def test_request_monitoring_status_coverage(self, signal_mock):
        # All types of edge cases.
        signal_mock.return_value = (
            ['x', None],
            ['y', list('~')],
            ['z', Exception()],
            ['!', MonitoringStatusIssue('', '', timezone.now())]
        )
        dsmr_backend.services.backend.request_monitoring_status()


@mock.patch('requests.get')
class TestIslatestVersion(TestCase):
    response_same_branch_unchanged = [
        {
            # Lowest in branch
            "tag_name": "v{}.0.0".format(settings.DSMRREADER_MAIN_BRANCH),
            "prerelease": False,
            "draft": False,
        },
        {
            # Current in branch
            "tag_name": '{}.{}.{}'.format(* settings.DSMRREADER_RAW_VERSION[:3]),
            "prerelease": False,
            "draft": False,
        },
        {
            # Latest but draft (should be ignored)
            "tag_name": "v10.99.1",
            "prerelease": False,
            "draft": True,
        },
        {
            # Latest but prerelease (should be ignored)
            "tag_name": "v10.99.2",
            "prerelease": True,
            "draft": False,
        }
    ]
    response_same_branch_newer_release = [
        {
            # Latest in branch
            "tag_name": "{}.99.0".format(settings.DSMRREADER_MAIN_BRANCH),
            "prerelease": False,
            "draft": False,
        }
    ]
    response_newer_branch = [
        {
            # Newer/other branch (should be ignored)
            "tag_name": "v10.99.0",
            "prerelease": False,
            "draft": False,
        }
    ]

    def test_same_releases_in_branch_available(self, get_mock):
        request_mock = mock.MagicMock()
        request_mock.json.return_value = self.response_same_branch_unchanged
        get_mock.return_value = request_mock

        self.assertTrue(dsmr_backend.services.backend.is_latest_version())

    def test_new_release_in_branch_available(self, get_mock):
        request_mock = mock.MagicMock()
        request_mock.json.return_value = self.response_same_branch_newer_release
        get_mock.return_value = request_mock

        self.assertFalse(dsmr_backend.services.backend.is_latest_version())

    def test_newer_branch_new_release_available(self, get_mock):
        request_mock = mock.MagicMock()
        request_mock.json.return_value = self.response_newer_branch
        get_mock.return_value = request_mock

        # Should ignore other branches
        self.assertTrue(dsmr_backend.services.backend.is_latest_version())


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


@mock.patch.dict('os.environ', dict(
    DJANGO_DATABASE_ENGINE='my-engine',
    DJANGO_DATABASE_HOST='my-host',
    DJANGO_DATABASE_PORT='11111',
    DJANGO_DATABASE_NAME='my-db',
    DJANGO_DATABASE_USER='my-user',
    DJANGO_DATABASE_PASSWORD='my-pass',
    DJANGO_DATABASE_CONN_MAX_AGE='111',
    DJANGO_TIME_ZONE='my-timezone',
    DJANGO_SECRET_KEY='my-secret-key',
    DJANGO_STATIC_URL='static-url',
    DJANGO_FORCE_SCRIPT_NAME='script',
    DJANGO_USE_X_FORWARDED_HOST='True',
    DJANGO_USE_X_FORWARDED_PORT='True',
    DJANGO_X_FRAME_OPTIONS='x-frame',
    DSMRREADER_LOGLEVEL='WARNING',  # Note: restricted choices
    DSMRREADER_PLUGINS='module1-path,module2-path'
))
class TestEnvSettings(InterceptCommandStdoutMixin, TestCase):
    def test_env(self):
        """
        WARNING: If these tests fail, first check whether you locally override (and break it) with LEGACY env vars!
        """
        importlib.reload(django_overrides)
        importlib.reload(settings_used)

        self.assertEqual(settings_used.DATABASES['default']['ENGINE'], 'my-engine')
        self.assertEqual(settings_used.DATABASES['default']['HOST'], 'my-host')
        self.assertEqual(settings_used.DATABASES['default']['PORT'], 11111)
        self.assertEqual(settings_used.DATABASES['default']['NAME'], 'my-db')
        self.assertEqual(settings_used.DATABASES['default']['USER'], 'my-user')
        self.assertEqual(settings_used.DATABASES['default']['PASSWORD'], 'my-pass')
        self.assertEqual(settings_used.DATABASES['default']['CONN_MAX_AGE'], 111)
        self.assertEqual(settings_used.SECRET_KEY, 'my-secret-key')
        self.assertEqual(settings_used.TIME_ZONE, 'my-timezone')
        self.assertEqual(settings_used.LOGGING['loggers']['dsmrreader']['level'], 'WARNING')
        self.assertEqual(settings_used.DSMRREADER_PLUGINS, ('module1-path', 'module2-path'))
        self.assertEqual(settings_used.STATIC_URL, 'static-url')
        self.assertEqual(settings_used.FORCE_SCRIPT_NAME, 'script')
        self.assertEqual(settings_used.USE_X_FORWARDED_HOST, True)
        self.assertEqual(settings_used.USE_X_FORWARDED_PORT, True)
        self.assertEqual(settings_used.X_FRAME_OPTIONS, 'x-frame')
