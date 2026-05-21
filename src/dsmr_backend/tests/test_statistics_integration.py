"""
Integration tests for statistics generation (issue #1770).

Tests the complete pipeline from unprocessed DsmrReadings through consumption
generation to DayStatistics and HourStatistics over a 48-hour period that
straddles two calendar days.

Most electricity assertions are tight enough (places=3) to expose two known bugs:

- Midnight-border gap: day_consumption() anchors on the first/last reading
  *within* the calendar day, losing the interval between the last reading of
  day D-1 and the first reading of day D.  This causes each day's total to be
  off by one ELECTRICITY_INCREMENT.

- N-1 off-by-one in HourStatistics: create_hourly_statistics() similarly
  captures (N-1) increments per hour instead of N.

Tests will fail on unfixed code and pass once the fixes are applied.
"""

from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.db.models import Sum
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
import dsmr_consumption.services
import dsmr_stats.services


class TestStatisticsIntegration(TestCase):
    """
    Integration test for issue #1770: complete pipeline over 48 hours.

    A seed reading at Jan 9 23:30 (one interval before the data starts) holds the
    initial meter positions before any increment.  It serves as the cross-midnight
    anchor_start for Jan 10, making it possible to assert gap-free daily totals.

    Main readings run from Jan 10 00:00 through Jan 11 23:30 at READINGS_PER_HOUR
    intervals.  A single extra reading on Jan 12 13:00 satisfies the stats
    generator's requirement for a gas reading on the day after the last complete day.
    """

    # Seed reading: last record before the data window starts.
    SEED_DATETIME = timezone.datetime(2020, 1, 9, 23, 30, 0)
    START_DATETIME = timezone.datetime(2020, 1, 10, 0, 0, 0)
    HOURS_TO_GENERATE = 48
    READINGS_PER_HOUR = 2  # One per 30 minutes (reduced for test speed)
    # Extra readings appended after the main block (midnight anchor + Jan 12 sentinel).
    # Subclasses may override when their data generation needs additional boundary readings.
    EXTRA_READINGS = 2

    ELECTRICITY_INCREMENT_1 = Decimal("0.001")  # kWh per reading
    ELECTRICITY_INCREMENT_2 = Decimal("0.002")
    ELECTRICITY_RETURNED_1 = Decimal("0.0005")
    ELECTRICITY_RETURNED_2 = Decimal("0.001")
    # v5 cumulative gas: last-first per hour = 1 increment → 24 × 0.050 = 1.2 m³/day
    GAS_INCREMENT = Decimal("0.050")

    # ------------------------------------------------------------------
    # Hooks for subclass variation (DSMR version, reading generator)
    # ------------------------------------------------------------------

    def _dsmr_version(self) -> str:
        return "50"

    def _generate_readings(self) -> None:
        self._generate_dsmr_readings()

    # ------------------------------------------------------------------
    # setUp
    # ------------------------------------------------------------------

    def setUp(self) -> None:
        EnergySupplierPrice.objects.create(
            start=timezone.datetime(2019, 1, 1).date(),
            end=timezone.datetime(2025, 1, 1).date(),
            description="Test Energy Price",
            electricity_delivered_1_price=Decimal("0.20"),
            electricity_delivered_2_price=Decimal("0.25"),
            electricity_returned_1_price=Decimal("0.10"),
            electricity_returned_2_price=Decimal("0.15"),
            gas_price=Decimal("0.80"),
            fixed_daily_cost=Decimal("0.50"),
        )

        MeterStatistics.get_solo()
        MeterStatistics.objects.all().update(dsmr_version=self._dsmr_version())

        consumption_settings = ConsumptionSettings.get_solo()
        consumption_settings.electricity_grouping_type = ConsumptionSettings.ELECTRICITY_GROUPING_BY_READING
        consumption_settings.save()

        self.consumption_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_GENERATE_CONSUMPTION)
        self.consumption_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

        self.stats_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_STATS_GENERATOR)
        self.stats_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

        self._generate_readings()

    # ------------------------------------------------------------------
    # Data generation
    # ------------------------------------------------------------------

    def _generate_dsmr_readings(self) -> None:
        """
        Create one seed reading at SEED_DATETIME followed by HOURS_TO_GENERATE hours
        of readings at READINGS_PER_HOUR intervals, plus one extra reading on Jan 12.

        The seed reading stores the initial meter positions (before any increment) and
        provides the cross-midnight anchor for Jan 10 once the fix is applied.
        Each subsequent reading increments all meter positions by the configured amounts.
        """
        seed_dt = timezone.make_aware(self.SEED_DATETIME)
        start_dt = timezone.make_aware(self.START_DATETIME)
        minutes_per_reading = 60 // self.READINGS_PER_HOUR
        total_readings = self.HOURS_TO_GENERATE * self.READINGS_PER_HOUR

        # Initial positions held by the seed reading (no increment yet).
        electricity_delivered_1 = Decimal("1000.000")
        electricity_delivered_2 = Decimal("2000.000")
        electricity_returned_1 = Decimal("100.000")
        electricity_returned_2 = Decimal("200.000")
        gas_delivered = Decimal("500.000")

        DsmrReading.objects.create(
            timestamp=seed_dt,
            electricity_delivered_1=electricity_delivered_1,
            electricity_returned_1=electricity_returned_1,
            electricity_delivered_2=electricity_delivered_2,
            electricity_returned_2=electricity_returned_2,
            electricity_currently_delivered=Decimal("0.500"),
            electricity_currently_returned=Decimal("0.100"),
            extra_device_timestamp=seed_dt,
            extra_device_delivered=gas_delivered,
            processed=False,
        )

        readings_to_create = []
        for i in range(total_readings):
            current_time = start_dt + timezone.timedelta(minutes=i * minutes_per_reading)
            electricity_delivered_1 += self.ELECTRICITY_INCREMENT_1
            electricity_delivered_2 += self.ELECTRICITY_INCREMENT_2
            electricity_returned_1 += self.ELECTRICITY_RETURNED_1
            electricity_returned_2 += self.ELECTRICITY_RETURNED_2
            gas_delivered += self.GAS_INCREMENT
            readings_to_create.append(
                DsmrReading(
                    timestamp=current_time,
                    electricity_delivered_1=electricity_delivered_1,
                    electricity_returned_1=electricity_returned_1,
                    electricity_delivered_2=electricity_delivered_2,
                    electricity_returned_2=electricity_returned_2,
                    electricity_currently_delivered=Decimal("0.500"),
                    electricity_currently_returned=Decimal("0.100"),
                    extra_device_timestamp=current_time,
                    extra_device_delivered=gas_delivered,
                    processed=False,
                )
            )
        DsmrReading.objects.bulk_create(readings_to_create)

        # Midnight reading at AMS Jan 12 00:00 (UTC Jan 11 23:00) — closes the last UTC hour of Jan 11
        # so create_hourly_statistics() has an anchor at both hour boundaries for that hour.
        midnight_time = start_dt + timezone.timedelta(hours=48)
        electricity_delivered_1 += self.ELECTRICITY_INCREMENT_1
        electricity_delivered_2 += self.ELECTRICITY_INCREMENT_2
        electricity_returned_1 += self.ELECTRICITY_RETURNED_1
        electricity_returned_2 += self.ELECTRICITY_RETURNED_2
        gas_delivered += self.GAS_INCREMENT
        DsmrReading.objects.create(
            timestamp=midnight_time,
            electricity_delivered_1=electricity_delivered_1,
            electricity_returned_1=electricity_returned_1,
            electricity_delivered_2=electricity_delivered_2,
            electricity_returned_2=electricity_returned_2,
            electricity_currently_delivered=Decimal("0.500"),
            electricity_currently_returned=Decimal("0.100"),
            extra_device_timestamp=midnight_time,
            extra_device_delivered=gas_delivered,
            processed=False,
        )

        # Extra reading on Jan 12 so the stats generator does not stall waiting
        # for a gas reading on the day after Jan 11.
        extra_time = start_dt + timezone.timedelta(hours=61)
        electricity_delivered_1 += self.ELECTRICITY_INCREMENT_1
        electricity_delivered_2 += self.ELECTRICITY_INCREMENT_2
        electricity_returned_1 += self.ELECTRICITY_RETURNED_1
        electricity_returned_2 += self.ELECTRICITY_RETURNED_2
        gas_delivered += self.GAS_INCREMENT
        DsmrReading.objects.create(
            timestamp=extra_time,
            electricity_delivered_1=electricity_delivered_1,
            electricity_returned_1=electricity_returned_1,
            electricity_delivered_2=electricity_delivered_2,
            electricity_returned_2=electricity_returned_2,
            electricity_currently_delivered=Decimal("0.500"),
            electricity_currently_returned=Decimal("0.100"),
            extra_device_timestamp=extra_time,
            extra_device_delivered=gas_delivered,
            processed=False,
        )

    # ------------------------------------------------------------------
    # Pipeline helpers
    # ------------------------------------------------------------------

    def _process_all_readings(self) -> None:
        """Process every unprocessed DsmrReading into consumption records."""
        while DsmrReading.objects.unprocessed().exists():
            dsmr_consumption.services.run(self.consumption_process)

    def _generate_all_statistics(self) -> None:
        """
        Drive the stats generator until it can make no further progress.
        Must be called inside a timezone.now mock; the scheduler uses timezone.now()
        to decide whether to reschedule rather than process.

        Iterates until no new DayStatistics were created in a pass *and* the process
        is scheduled in the future (i.e., it is genuinely waiting for new data).
        """
        for _ in range(self.HOURS_TO_GENERATE // 24 + 3):
            prev_count = DayStatistics.objects.count()
            dsmr_stats.services.run(self.stats_process)
            self.stats_process.refresh_from_db()
            if DayStatistics.objects.count() == prev_count and self.stats_process.planned > timezone.now():
                break

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_reading_generation(self) -> None:
        """Seed + main block + extra = expected total; timestamps are correct."""
        # 1 seed + (HOURS_TO_GENERATE × READINGS_PER_HOUR) main + EXTRA_READINGS
        expected_total = 1 + self.HOURS_TO_GENERATE * self.READINGS_PER_HOUR + self.EXTRA_READINGS
        self.assertEqual(DsmrReading.objects.count(), expected_total)
        self.assertEqual(DsmrReading.objects.unprocessed().count(), expected_total)

        seed = DsmrReading.objects.order_by("timestamp").first()
        self.assertEqual(seed.timestamp, timezone.make_aware(self.SEED_DATETIME))

        first_main = DsmrReading.objects.order_by("timestamp")[1]
        self.assertEqual(first_main.timestamp, timezone.make_aware(self.START_DATETIME))

    @mock.patch("django.utils.timezone.now")
    def test_full_statistics_integration(self, now_mock: mock.Mock) -> None:
        """
        Full pipeline: readings → consumption → HourStatistics → DayStatistics.

        Verifies record counts at each stage, then delegates value assertions
        to the focused _verify_* helpers.
        """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 1, 14, 12, 0, 0))

        expected_record_count = 1 + self.HOURS_TO_GENERATE * self.READINGS_PER_HOUR + self.EXTRA_READINGS
        self.assertEqual(DsmrReading.objects.unprocessed().count(), expected_record_count)
        self.assertEqual(ElectricityConsumption.objects.count(), 0)
        self.assertEqual(GasConsumption.objects.count(), 0)
        self.assertEqual(DayStatistics.objects.count(), 0)
        self.assertEqual(HourStatistics.objects.count(), 0)

        self._process_all_readings()
        self.assertEqual(DsmrReading.objects.unprocessed().count(), 0)
        # Per-reading grouping: one ElectricityConsumption per DsmrReading.
        self.assertEqual(ElectricityConsumption.objects.count(), expected_record_count)
        self.assertGreater(GasConsumption.objects.count(), 0)

        self._generate_all_statistics()

        # Jan 10 and Jan 11 — two complete days with full data.
        # (The seed reading on Jan 9 also produces a Jan 9 day stat, which is ignored here.)
        jan_10 = timezone.datetime(2020, 1, 10).date()
        jan_12 = timezone.datetime(2020, 1, 12).date()
        self.assertEqual(DayStatistics.objects.filter(day__gte=jan_10, day__lt=jan_12).count(), 2)
        self.assertEqual(
            HourStatistics.objects.filter(hour_start__date__gte=jan_10, hour_start__date__lt=jan_12).count(),
            self.HOURS_TO_GENERATE,
        )

        self._verify_day_statistics()
        self._verify_hour_statistics()
        self._verify_hour_day_consistency()

    @mock.patch("django.utils.timezone.now")
    def test_midnight_border_gap(self, now_mock: mock.Mock) -> None:
        """
        No electricity consumption is lost at day boundaries.

        Summing electricity1 (and electricity2) across all DayStatistics must
        equal the meter-position delta from the seed ElectricityConsumption record
        (last record before Jan 10 00:00) to the final record of the last complete
        day.

        With the current buggy day_consumption() the delta between the last reading
        of day D-1 and the first reading of day D is silently dropped, so the sum
        falls short by one ELECTRICITY_INCREMENT per day boundary crossed.
        """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 1, 14, 12, 0, 0))

        self._process_all_readings()
        self._generate_all_statistics()

        seed_ec = ElectricityConsumption.objects.order_by("read_at").first()
        end_of_jan_11 = timezone.make_aware(timezone.datetime(2020, 1, 11, 23, 59, 59))
        final_ec = ElectricityConsumption.objects.filter(read_at__lte=end_of_jan_11).order_by("read_at").last()

        expected_elec1 = final_ec.delivered_1 - seed_ec.delivered_1
        expected_elec2 = final_ec.delivered_2 - seed_ec.delivered_2

        totals = DayStatistics.objects.aggregate(elec1=Sum("electricity1"), elec2=Sum("electricity2"))

        self.assertAlmostEqual(
            float(totals["elec1"]),
            float(expected_elec1),
            places=3,
            msg="Electricity1 lost at day boundaries (midnight-border gap)",
        )
        self.assertAlmostEqual(
            float(totals["elec2"]),
            float(expected_elec2),
            places=3,
            msg="Electricity2 lost at day boundaries (midnight-border gap)",
        )

    @mock.patch("django.utils.timezone.now")
    def test_gas_totals_accuracy(self, now_mock: mock.Mock) -> None:
        """Each day's gas total equals the sum of its HourStatistics gas values (issue #1770)."""
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 1, 14, 12, 0, 0))

        self._process_all_readings()
        self._generate_all_statistics()

        jan_10 = timezone.datetime(2020, 1, 10).date()
        jan_12 = timezone.datetime(2020, 1, 12).date()
        for day_stat in DayStatistics.objects.filter(day__gte=jan_10, day__lt=jan_12):
            day_start = timezone.make_aware(
                timezone.datetime(year=day_stat.day.year, month=day_stat.day.month, day=day_stat.day.day)
            )
            day_end = day_start + timezone.timedelta(hours=24)
            hour_gas_sum = HourStatistics.objects.filter(
                hour_start__gte=day_start,
                hour_start__lt=day_end,
            ).aggregate(
                total=Sum("gas")
            )["total"]

            self.assertAlmostEqual(
                float(day_stat.gas),
                float(hour_gas_sum),
                places=2,
                msg=f"Day gas does not match hour sum for {day_stat.day} (issue #1770)",
            )

    # ------------------------------------------------------------------
    # Shared assertion helpers (called from test_full_statistics_integration)
    # ------------------------------------------------------------------

    def _verify_day_statistics(self) -> None:
        """Each complete day's electricity totals must equal increment × readings_per_day."""
        readings_per_day = 24 * self.READINGS_PER_HOUR
        expected_elec1 = self.ELECTRICITY_INCREMENT_1 * readings_per_day
        expected_elec2 = self.ELECTRICITY_INCREMENT_2 * readings_per_day
        expected_elec1_returned = self.ELECTRICITY_RETURNED_1 * readings_per_day
        expected_elec2_returned = self.ELECTRICITY_RETURNED_2 * readings_per_day

        jan_10 = timezone.datetime(2020, 1, 10).date()
        jan_12 = timezone.datetime(2020, 1, 12).date()
        for day_stat in DayStatistics.objects.filter(day__gte=jan_10, day__lt=jan_12):
            self.assertAlmostEqual(
                float(day_stat.electricity1), float(expected_elec1), places=3, msg=f"electricity1 {day_stat.day}"
            )
            self.assertAlmostEqual(
                float(day_stat.electricity2), float(expected_elec2), places=3, msg=f"electricity2 {day_stat.day}"
            )
            self.assertAlmostEqual(
                float(day_stat.electricity1_returned),
                float(expected_elec1_returned),
                places=3,
                msg=f"electricity1_returned {day_stat.day}",
            )
            self.assertAlmostEqual(
                float(day_stat.electricity2_returned),
                float(expected_elec2_returned),
                places=3,
                msg=f"electricity2_returned {day_stat.day}",
            )
            # Gas: reasonableness bounds only — boundary attribution is inherently ambiguous.
            self.assertGreater(float(day_stat.gas), 1.0, msg=f"gas too low for {day_stat.day}")
            self.assertLess(float(day_stat.gas), 2.0, msg=f"gas too high for {day_stat.day}")

    def _verify_hour_statistics(self) -> None:
        """Each hour's electricity totals must equal increment × READINGS_PER_HOUR."""
        expected_elec1 = self.ELECTRICITY_INCREMENT_1 * self.READINGS_PER_HOUR
        expected_elec2 = self.ELECTRICITY_INCREMENT_2 * self.READINGS_PER_HOUR
        expected_elec1_returned = self.ELECTRICITY_RETURNED_1 * self.READINGS_PER_HOUR
        expected_elec2_returned = self.ELECTRICITY_RETURNED_2 * self.READINGS_PER_HOUR

        jan_10 = timezone.datetime(2020, 1, 10).date()
        jan_12 = timezone.datetime(2020, 1, 12).date()
        for hour_stat in HourStatistics.objects.filter(hour_start__date__gte=jan_10, hour_start__date__lt=jan_12):
            self.assertAlmostEqual(
                float(hour_stat.electricity1),
                float(expected_elec1),
                places=3,
                msg=f"electricity1 {hour_stat.hour_start}",
            )
            self.assertAlmostEqual(
                float(hour_stat.electricity2),
                float(expected_elec2),
                places=3,
                msg=f"electricity2 {hour_stat.hour_start}",
            )
            self.assertAlmostEqual(
                float(hour_stat.electricity1_returned),
                float(expected_elec1_returned),
                places=3,
                msg=f"electricity1_returned {hour_stat.hour_start}",
            )
            self.assertAlmostEqual(
                float(hour_stat.electricity2_returned),
                float(expected_elec2_returned),
                places=3,
                msg=f"electricity2_returned {hour_stat.hour_start}",
            )
            self.assertGreaterEqual(float(hour_stat.gas), 0, msg=f"gas negative for {hour_stat.hour_start}")

    def _verify_hour_day_consistency(self) -> None:
        """Sum of each complete day's HourStatistics must match its DayStatistics values."""
        jan_10 = timezone.datetime(2020, 1, 10).date()
        jan_12 = timezone.datetime(2020, 1, 12).date()
        for day_stat in DayStatistics.objects.filter(day__gte=jan_10, day__lt=jan_12):
            day_start = timezone.make_aware(
                timezone.datetime(year=day_stat.day.year, month=day_stat.day.month, day=day_stat.day.day)
            )
            day_end = day_start + timezone.timedelta(hours=24)
            hour_totals = HourStatistics.objects.filter(
                hour_start__gte=day_start,
                hour_start__lt=day_end,
            ).aggregate(
                elec1=Sum("electricity1"),
                elec2=Sum("electricity2"),
                elec1_returned=Sum("electricity1_returned"),
                elec2_returned=Sum("electricity2_returned"),
                gas=Sum("gas"),
            )

            self.assertAlmostEqual(
                float(hour_totals["elec1"]),
                float(day_stat.electricity1),
                places=2,
                msg=f"Hour sum electricity1 != day total for {day_stat.day}",
            )
            self.assertAlmostEqual(
                float(hour_totals["elec2"]),
                float(day_stat.electricity2),
                places=2,
                msg=f"Hour sum electricity2 != day total for {day_stat.day}",
            )
            self.assertAlmostEqual(
                float(hour_totals["elec1_returned"]),
                float(day_stat.electricity1_returned),
                places=2,
                msg=f"Hour sum electricity1_returned != day total for {day_stat.day}",
            )
            self.assertAlmostEqual(
                float(hour_totals["elec2_returned"]),
                float(day_stat.electricity2_returned),
                places=2,
                msg=f"Hour sum electricity2_returned != day total for {day_stat.day}",
            )
            self.assertAlmostEqual(
                float(hour_totals["gas"]),
                float(day_stat.gas),
                places=2,
                msg=f"Hour sum gas != day total for {day_stat.day} (issue #1770)",
            )


class TestStatisticsIntegrationDSMRv4(TestStatisticsIntegration):
    """
    Same integration tests for DSMR v4 gas readings.

    In DSMR v4, gas is reported as a per-hour delta (currently_delivered) updated
    once per hour, rather than as a cumulative position updated every reading.
    Only _dsmr_version(), _generate_readings(), and _verify_hour_statistics() differ
    from the base class.
    """

    # Fixed per-hour gas delta for v4 (independent of READINGS_PER_HOUR).
    GAS_V4_PER_HOUR = Decimal("0.060")
    # v4 shifts gas timestamps back 1 hour, so the last hour of the last complete day
    # needs a boundary reading at exactly HOURS_TO_GENERATE hours after START_DATETIME.
    EXTRA_READINGS = 2

    def _dsmr_version(self) -> str:
        return "42"

    def _generate_readings(self) -> None:
        self._generate_dsmr_readings_v4()

    def _generate_dsmr_readings_v4(self) -> None:
        """
        Create one seed reading at SEED_DATETIME followed by HOURS_TO_GENERATE hours
        of readings in DSMR v4 style, plus one extra reading on Jan 12.

        Gas is updated once per hour (at the first reading of each hour) rather
        than every reading.  extra_device_delivered is None for non-gas readings.
        """
        seed_dt = timezone.make_aware(self.SEED_DATETIME)
        start_dt = timezone.make_aware(self.START_DATETIME)
        minutes_per_reading = 60 // self.READINGS_PER_HOUR
        total_readings = self.HOURS_TO_GENERATE * self.READINGS_PER_HOUR

        electricity_delivered_1 = Decimal("1000.000")
        electricity_delivered_2 = Decimal("2000.000")
        electricity_returned_1 = Decimal("100.000")
        electricity_returned_2 = Decimal("200.000")
        gas_delivered = Decimal("500.000")

        DsmrReading.objects.create(
            timestamp=seed_dt,
            electricity_delivered_1=electricity_delivered_1,
            electricity_returned_1=electricity_returned_1,
            electricity_delivered_2=electricity_delivered_2,
            electricity_returned_2=electricity_returned_2,
            electricity_currently_delivered=Decimal("0.500"),
            electricity_currently_returned=Decimal("0.100"),
            extra_device_timestamp=seed_dt,
            extra_device_delivered=gas_delivered,
            processed=False,
        )

        readings_to_create = []
        last_gas_timestamp = None
        for i in range(total_readings):
            current_time = start_dt + timezone.timedelta(minutes=i * minutes_per_reading)
            electricity_delivered_1 += self.ELECTRICITY_INCREMENT_1
            electricity_delivered_2 += self.ELECTRICITY_INCREMENT_2
            electricity_returned_1 += self.ELECTRICITY_RETURNED_1
            electricity_returned_2 += self.ELECTRICITY_RETURNED_2

            # DSMR v4: gas updates once per hour at the first reading of each hour.
            is_first_in_hour = i % self.READINGS_PER_HOUR == 0
            if is_first_in_hour:
                gas_delivered += self.GAS_V4_PER_HOUR
                last_gas_timestamp = current_time

            readings_to_create.append(
                DsmrReading(
                    timestamp=current_time,
                    electricity_delivered_1=electricity_delivered_1,
                    electricity_returned_1=electricity_returned_1,
                    electricity_delivered_2=electricity_delivered_2,
                    electricity_returned_2=electricity_returned_2,
                    electricity_currently_delivered=Decimal("0.500"),
                    electricity_currently_returned=Decimal("0.100"),
                    extra_device_timestamp=last_gas_timestamp,
                    extra_device_delivered=gas_delivered if is_first_in_hour else None,
                    processed=False,
                )
            )
        DsmrReading.objects.bulk_create(readings_to_create)

        # Intermediate extra reading at Jan 12 00:00 (exactly HOURS_TO_GENERATE hours after start).
        # In DSMR v4, _compact_gas() shifts gas timestamps back 1 hour, so this reading's
        # gas (timestamped Jan 12 00:00+01:00) is stored as GasConsumption at Jan 11 23:00+01:00,
        # filling the last hour [23:00, 00:00) of Jan 11 which otherwise has no gas entry.
        intermediate_time = start_dt + timezone.timedelta(hours=self.HOURS_TO_GENERATE)
        electricity_delivered_1 += self.ELECTRICITY_INCREMENT_1
        electricity_delivered_2 += self.ELECTRICITY_INCREMENT_2
        electricity_returned_1 += self.ELECTRICITY_RETURNED_1
        electricity_returned_2 += self.ELECTRICITY_RETURNED_2
        gas_delivered += self.GAS_V4_PER_HOUR
        DsmrReading.objects.create(
            timestamp=intermediate_time,
            electricity_delivered_1=electricity_delivered_1,
            electricity_returned_1=electricity_returned_1,
            electricity_delivered_2=electricity_delivered_2,
            electricity_returned_2=electricity_returned_2,
            electricity_currently_delivered=Decimal("0.500"),
            electricity_currently_returned=Decimal("0.100"),
            extra_device_timestamp=intermediate_time,
            extra_device_delivered=gas_delivered,
            processed=False,
        )

        extra_time = start_dt + timezone.timedelta(hours=61)
        electricity_delivered_1 += self.ELECTRICITY_INCREMENT_1
        electricity_delivered_2 += self.ELECTRICITY_INCREMENT_2
        electricity_returned_1 += self.ELECTRICITY_RETURNED_1
        electricity_returned_2 += self.ELECTRICITY_RETURNED_2
        gas_delivered += self.GAS_V4_PER_HOUR
        DsmrReading.objects.create(
            timestamp=extra_time,
            electricity_delivered_1=electricity_delivered_1,
            electricity_returned_1=electricity_returned_1,
            electricity_delivered_2=electricity_delivered_2,
            electricity_returned_2=electricity_returned_2,
            electricity_currently_delivered=Decimal("0.500"),
            electricity_currently_returned=Decimal("0.100"),
            extra_device_timestamp=extra_time,
            extra_device_delivered=gas_delivered,
            processed=False,
        )

    def _verify_hour_statistics(self) -> None:
        """DSMR v4: electricity same as v5; gas must equal GAS_V4_PER_HOUR per hour."""
        expected_elec1 = self.ELECTRICITY_INCREMENT_1 * self.READINGS_PER_HOUR
        expected_elec2 = self.ELECTRICITY_INCREMENT_2 * self.READINGS_PER_HOUR
        expected_elec1_returned = self.ELECTRICITY_RETURNED_1 * self.READINGS_PER_HOUR
        expected_elec2_returned = self.ELECTRICITY_RETURNED_2 * self.READINGS_PER_HOUR

        jan_10 = timezone.datetime(2020, 1, 10).date()
        jan_12 = timezone.datetime(2020, 1, 12).date()
        for hour_stat in HourStatistics.objects.filter(hour_start__date__gte=jan_10, hour_start__date__lt=jan_12):
            self.assertAlmostEqual(
                float(hour_stat.electricity1),
                float(expected_elec1),
                places=3,
                msg=f"electricity1 {hour_stat.hour_start}",
            )
            self.assertAlmostEqual(
                float(hour_stat.electricity2),
                float(expected_elec2),
                places=3,
                msg=f"electricity2 {hour_stat.hour_start}",
            )
            self.assertAlmostEqual(
                float(hour_stat.electricity1_returned),
                float(expected_elec1_returned),
                places=3,
                msg=f"electricity1_returned {hour_stat.hour_start}",
            )
            self.assertAlmostEqual(
                float(hour_stat.electricity2_returned),
                float(expected_elec2_returned),
                places=3,
                msg=f"electricity2_returned {hour_stat.hour_start}",
            )
            self.assertAlmostEqual(
                float(hour_stat.gas),
                float(self.GAS_V4_PER_HOUR),
                places=3,
                msg=f"gas {hour_stat.hour_start}",
            )
