from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import QuarterHourPeakElectricityConsumption
import dsmr_consumption.services


class TestServices(InterceptCommandStdoutMixin, TestCase):
    def setUp(self):
        self.schedule_process = ScheduledProcess.objects.get(
            module=settings.DSMRREADER_MODULE_CALCULATE_QUARTER_HOUR_PEAKS
        )
        self.assertTrue(self.schedule_process.active)

    def test_no_readings(self):
        self.assertFalse(DsmrReading.objects.all().exists())
        self.assertFalse(QuarterHourPeakElectricityConsumption.objects.all().exists())
        dsmr_consumption.services.run_quarter_hour_peaks(self.schedule_process)

        self.assertFalse(QuarterHourPeakElectricityConsumption.objects.all().exists())

    def _create_reading1(self) -> DsmrReading:
        return DsmrReading.objects.create(
            timestamp=timezone.make_aware(timezone.datetime(2022, 1, 1, hour=14, minute=15, second=1)),
            electricity_delivered_1=100,
            electricity_delivered_2=150,
            electricity_returned_1=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )

    def _create_reading2(self) -> DsmrReading:
        return DsmrReading.objects.create(
            timestamp=timezone.make_aware(timezone.datetime(2022, 1, 1, hour=14, minute=29, second=40)),
            electricity_delivered_1=150,
            electricity_delivered_2=250,
            # Return should not affect peak calculations at all
            electricity_returned_1=50,
            electricity_returned_2=100,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )

    def _create_post_reading(self, reading2: DsmrReading) -> DsmrReading:
        return DsmrReading.objects.create(
            timestamp=reading2.timestamp + timezone.timedelta(minutes=15),
            electricity_delivered_1=0,
            electricity_delivered_2=0,
            electricity_returned_1=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )

    @mock.patch('django.utils.timezone.now')
    def test_okay(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2022, 1, 1, hour=14, minute=34, second=0))
        self.schedule_process.reschedule(timezone.now())

        reading1 = self._create_reading1()
        reading2 = self._create_reading2()

        self.assertFalse(QuarterHourPeakElectricityConsumption.objects.all().exists())
        dsmr_consumption.services.run_quarter_hour_peaks(self.schedule_process)

        # Still lacking a new reading.
        self.assertFalse(QuarterHourPeakElectricityConsumption.objects.all().exists())
        self.assertEqual(
            self.schedule_process.planned,
            timezone.now() + timezone.timedelta(seconds=5)  # Postponed + X secs
        )

        # Create any reading after end.
        self._create_post_reading(reading2)

        # Retry.
        self.schedule_process.reschedule(timezone.now())
        dsmr_consumption.services.run_quarter_hour_peaks(self.schedule_process)

        self.assertEqual(QuarterHourPeakElectricityConsumption.objects.count(), 1)
        quarter_hour_peak = QuarterHourPeakElectricityConsumption.objects.get()
        self.assertEqual(quarter_hour_peak.read_at_start, reading1.timestamp)
        self.assertEqual(quarter_hour_peak.read_at_end, reading2.timestamp)
        self.assertEqual(quarter_hour_peak.duration, timezone.timedelta(minutes=14, seconds=39))  # = 15m - 21s
        self.assertEqual(
            quarter_hour_peak.average_delivered,
            # 150 kW for 879 seconds, but align with full hour (= 150 x ~4.09556314). 15m would be 3600 / 900 = 4x.
            Decimal('614.334')
        )

        # Retry again does nothing.
        self.schedule_process.reschedule(timezone.now())
        dsmr_consumption.services.run_quarter_hour_peaks(self.schedule_process)
        self.assertEqual(QuarterHourPeakElectricityConsumption.objects.count(), 1)  # Same

    @mock.patch('django.utils.timezone.now')
    def test_too_few_readings(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2022, 1, 1, hour=14, minute=34, second=0))
        self.schedule_process.reschedule(timezone.now())

        reading1 = self._create_reading1()
        # reading 2 is not created within the same quarter.
        self._create_post_reading(reading1)

        dsmr_consumption.services.run_quarter_hour_peaks(self.schedule_process)

        # Nothing should happen.
        self.assertEqual(QuarterHourPeakElectricityConsumption.objects.count(), 0)
        self.assertEqual(
            self.schedule_process.planned,
            timezone.now() + timezone.timedelta(minutes=15)  # Postponed + X minutes
        )

    @mock.patch('django.utils.timezone.now')
    def test_retroactive(self, now_mock):
        """ Ensure it should work retroactively as well. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2022, 1, 1, hour=0, minute=0, second=0))

        MAX_INTERVAL = 300
        self.schedule_process.reschedule(timezone.now() - timezone.timedelta(minutes=MAX_INTERVAL))  # Schedule once

        for interval in range(0, MAX_INTERVAL, 5):
            DsmrReading.objects.create(
                timestamp=timezone.now() - timezone.timedelta(minutes=interval),
                electricity_delivered_1=100 + 0.2 * interval,
                electricity_delivered_2=150 + 0.2 * interval,
                electricity_returned_1=0,
                electricity_returned_2=0,
                electricity_currently_delivered=0,
                electricity_currently_returned=0,
            )

        self.assertFalse(QuarterHourPeakElectricityConsumption.objects.all().exists())

        for _ in range(0, MAX_INTERVAL, 5):
            dsmr_consumption.services.run_quarter_hour_peaks(self.schedule_process)

        self.assertEqual(QuarterHourPeakElectricityConsumption.objects.count(), 20)
