from datetime import datetime
from unittest import mock
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.settings import RetentionSettings
import dsmr_datalogger.services.retention


_LOCMEM_CACHE = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": "retention-test"}}


class TestRetention(TestCase):
    fixtures = [
        "dsmr_datalogger/dsmrreading.json",
        "dsmr_datalogger/electricity-consumption.json",
        "dsmr_datalogger/gas-consumption.json",
    ]
    schedule_process = None

    def setUp(self):
        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_RETENTION_DATA_ROTATION)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

        RetentionSettings.get_solo()
        RetentionSettings.objects.update(data_retention_in_hours=None)  # Legacy tests: This used to be the default.
        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

    @mock.patch("django.utils.timezone.now")
    def test_disabled(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

        # Disabled settings should disable the process too.
        self.schedule_process.refresh_from_db()
        self.assertFalse(self.schedule_process.active)

    @mock.patch("django.utils.timezone.now")
    def test_enabled_with_cleanup(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        # Retention active, but point of retention not yet passed.
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_YEAR)
        RetentionSettings.get_solo().save()  # Trigger hook, faking interface action.

        dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

        # Allow point of retention to pass.
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_WEEK)
        RetentionSettings.get_solo().save()  # Trigger hook, faking interface action.

        # Should affect data now.
        dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.count(), 2)
        self.assertEqual(ElectricityConsumption.objects.count(), 8)
        self.assertEqual(GasConsumption.objects.count(), 32)

        # Make sure that specific data is kept.
        for x in [5629376, 5629427]:
            self.assertTrue(DsmrReading.objects.filter(pk=x).exists())

        for x in [95, 154, 155, 214, 215, 216, 217, 218]:
            self.assertTrue(ElectricityConsumption.objects.filter(pk=x).exists())

        self.assertFalse(GasConsumption.objects.filter(pk=32).exists())

        # Batch was not saturated, so the process should be delayed (no more data expected imminently).
        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=12))

    @mock.patch("django.utils.timezone.now")
    def test_enabled_no_cleanup(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        # Clean.
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_WEEK)
        dsmr_datalogger.services.retention.run(self.schedule_process)

        # No effect calling multiple times.
        dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.count(), 2)
        self.assertEqual(ElectricityConsumption.objects.count(), 8)
        self.assertEqual(GasConsumption.objects.count(), 32)

        # Should be delayed for a few hours now, nothing to do.
        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=12))


class TestRetentionCache(TestCase):
    fixtures = [
        "dsmr_datalogger/dsmrreading.json",
        "dsmr_datalogger/electricity-consumption.json",
        "dsmr_datalogger/gas-consumption.json",
    ]

    def setUp(self):
        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_RETENTION_DATA_ROTATION)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))
        RetentionSettings.get_solo()
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_WEEK)

    @override_settings(CACHES=_LOCMEM_CACHE, DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN=1)
    @mock.patch("django.utils.timezone.now")
    def test_saturated_batch_sets_cache_and_does_not_delay(self, now_mock):
        """A saturated batch stores a lower bound in the cache and does not delay the process."""
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        dsmr_datalogger.services.retention.run(self.schedule_process)

        # DsmrReading has 52 records in one hour — that hour saturates the batch of 1.
        self.assertIsNotNone(cache.get(dsmr_datalogger.services.retention._cache_key("DsmrReading")))

        # Process must not be delayed when the batch was saturated.
        self.schedule_process.refresh_from_db()
        self.assertNotEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=12))

    @override_settings(CACHES=_LOCMEM_CACHE)
    @mock.patch("django.utils.timezone.now")
    def test_cache_lower_bound_filters_already_processed(self, now_mock):
        """A pre-seeded lower bound causes the query to skip hours already processed."""
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        # Set a lower bound beyond the retention cutoff — combined with timestamp__lt=retention_date
        # this makes the query unsatisfiable, so nothing is found.
        future_bound = datetime(2017, 1, 1, tzinfo=ZoneInfo("UTC"))
        for model_name in ["DsmrReading", "ElectricityConsumption", "GasConsumption"]:
            cache.set(dsmr_datalogger.services.retention._cache_key(model_name), future_bound)

        dsmr_datalogger.services.retention.run(self.schedule_process)

        # Lower bound filtered everything — no records deleted.
        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

        # Cache entries are left untouched when nothing was found (lower bound is preserved).
        for model_name in ["DsmrReading", "ElectricityConsumption", "GasConsumption"]:
            self.assertEqual(
                cache.get(dsmr_datalogger.services.retention._cache_key(model_name)), future_bound
            )

        # Process delayed since there was nothing to clean.
        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=12))

    @override_settings(CACHES=_LOCMEM_CACHE)
    def test_clear_cache(self):
        """clear_cache() removes all retention lower bound entries."""
        for model_name in ["DsmrReading", "ElectricityConsumption", "GasConsumption"]:
            cache.set(dsmr_datalogger.services.retention._cache_key(model_name), "sentinel")

        dsmr_datalogger.services.retention.clear_cache()

        for model_name in ["DsmrReading", "ElectricityConsumption", "GasConsumption"]:
            self.assertIsNone(cache.get(dsmr_datalogger.services.retention._cache_key(model_name)))

    @override_settings(CACHES=_LOCMEM_CACHE)
    def test_retention_settings_save_clears_cache(self):
        """Saving RetentionSettings triggers the post_save signal which clears the cache."""
        for model_name in ["DsmrReading", "ElectricityConsumption", "GasConsumption"]:
            cache.set(dsmr_datalogger.services.retention._cache_key(model_name), "sentinel")

        RetentionSettings.get_solo().save()

        for model_name in ["DsmrReading", "ElectricityConsumption", "GasConsumption"]:
            self.assertIsNone(cache.get(dsmr_datalogger.services.retention._cache_key(model_name)))
