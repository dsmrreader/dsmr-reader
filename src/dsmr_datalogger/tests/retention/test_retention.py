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
            self.assertEqual(cache.get(dsmr_datalogger.services.retention._cache_key(model_name)), future_bound)

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


@override_settings(TIME_ZONE="Europe/Amsterdam", CACHES=_LOCMEM_CACHE)
class TestRetentionDSTFallBack(TestCase):
    """Regression test for #2137: retention must handle DST fall-back correctly on non-UTC systems.

    During Amsterdam DST fall-back (2016-10-30 01:00 UTC / 03:00 CEST → 02:00 CET), two
    distinct UTC hours (00:xx and 01:xx) both map to Amsterdam local hour 02:xx.

    Without tzinfo=UTC on TruncHour the ORM groups both UTC hours into one Amsterdam hour on
    PostgreSQL (where TruncHour becomes DATE_TRUNC driven by settings.TIME_ZONE, not the
    activated timezone). This causes the code to either loop indefinitely (pre-cache version)
    or silently skip the second UTC hour (post-cache version). Either way the records in the
    fall-back hour are never correctly thinned.

    Note: SQLite executes TruncHour in Python where timezone.activate() is effective, so the
    DST grouping bug does not manifest there. The test_trunchour_uses_explicit_utc test below
    therefore guards the fix at the implementation level across all backends.
    """

    def setUp(self) -> None:
        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_RETENTION_DATA_ROTATION)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))  # type: ignore[attr-defined]
        RetentionSettings.get_solo()
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_WEEK)

    def _make_reading(self, ts: datetime) -> None:
        DsmrReading.objects.create(
            timestamp=ts,
            processed=True,
            electricity_delivered_1=0,
            electricity_returned_1=0,
            electricity_delivered_2=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )

    @mock.patch("django.utils.timezone.now")
    def test_dst_fallback_both_utc_hours_thinned(self, now_mock: mock.MagicMock) -> None:
        """Both UTC hours spanning the DST fall-back must each be thinned to ITEM_COUNT_PER_HOUR.

        This test exercises the correct end-to-end behaviour on PostgreSQL. On SQLite the
        grouping is always UTC-correct regardless, so this test is primarily meaningful as a
        PostgreSQL integration check and as documentation of the scenario.
        """
        # One week after the DST transition — all Oct 30 records are past the retention cutoff.
        now_mock.return_value = datetime(2016, 11, 7, 0, 0, 0, tzinfo=ZoneInfo("UTC"))

        # Five readings in UTC 00:xx (= Amsterdam 02:xx CEST, before the clock falls back).
        # Five readings in UTC 01:xx (= Amsterdam 02:xx CET, after the clock falls back).
        # Both sets occupy the same Amsterdam local hour, which is what triggers #2137.
        for minute in range(0, 50, 10):
            self._make_reading(datetime(2016, 10, 30, 0, minute, tzinfo=ZoneInfo("UTC")))
            self._make_reading(datetime(2016, 10, 30, 1, minute, tzinfo=ZoneInfo("UTC")))

        self.assertEqual(DsmrReading.objects.count(), 10)

        dsmr_datalogger.services.retention.run(self.schedule_process)

        # Each of the two UTC hours must be independently reduced to ITEM_COUNT_PER_HOUR (2).
        self.assertEqual(DsmrReading.objects.count(), 4)
        self.assertEqual(
            DsmrReading.objects.filter(
                timestamp__gte=datetime(2016, 10, 30, 0, 0, tzinfo=ZoneInfo("UTC")),
                timestamp__lt=datetime(2016, 10, 30, 1, 0, tzinfo=ZoneInfo("UTC")),
            ).count(),
            2,
            "UTC hour 00:xx must be thinned to ITEM_COUNT_PER_HOUR",
        )
        self.assertEqual(
            DsmrReading.objects.filter(
                timestamp__gte=datetime(2016, 10, 30, 1, 0, tzinfo=ZoneInfo("UTC")),
                timestamp__lt=datetime(2016, 10, 30, 2, 0, tzinfo=ZoneInfo("UTC")),
            ).count(),
            2,
            "UTC hour 01:xx must be thinned to ITEM_COUNT_PER_HOUR",
        )

        # A second run must find nothing left to clean — the process converged.
        dsmr_datalogger.services.retention.run(self.schedule_process)
        self.assertEqual(DsmrReading.objects.count(), 4)
        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=12))  # type: ignore[attr-defined]

    @mock.patch("django.utils.timezone.now")
    def test_trunchour_uses_explicit_utc(self, now_mock: mock.MagicMock) -> None:
        """TruncHour must always be instantiated with tzinfo=ZoneInfo('UTC').

        This guards the fix at the implementation level: on PostgreSQL, TruncHour without an
        explicit tzinfo uses settings.TIME_ZONE (Europe/Amsterdam) rather than the activated
        timezone, producing wrong DST-era groupings. Passing tzinfo=ZoneInfo('UTC') explicitly
        overrides that and ensures correct UTC hour boundaries on every backend.
        """
        now_mock.return_value = datetime(2016, 11, 7, 0, 0, 0, tzinfo=ZoneInfo("UTC"))
        self._make_reading(datetime(2016, 10, 30, 0, 0, tzinfo=ZoneInfo("UTC")))
        self._make_reading(datetime(2016, 10, 30, 0, 30, tzinfo=ZoneInfo("UTC")))
        self._make_reading(datetime(2016, 10, 30, 0, 59, tzinfo=ZoneInfo("UTC")))

        utc = ZoneInfo("UTC")
        original_trunchour = dsmr_datalogger.services.retention.TruncHour

        captured: list[dict] = []

        def spy_trunchour(*args, **kwargs):  # type: ignore[no-untyped-def]
            captured.append({"args": args, "kwargs": kwargs})
            return original_trunchour(*args, **kwargs)

        with mock.patch.object(dsmr_datalogger.services.retention, "TruncHour", side_effect=spy_trunchour):
            dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertTrue(captured, "TruncHour was never called")
        for call in captured:
            self.assertEqual(
                call["kwargs"].get("tzinfo"),
                utc,
                "TruncHour must be called with tzinfo=ZoneInfo('UTC') to avoid DST grouping bugs on PostgreSQL (#2137)",
            )
