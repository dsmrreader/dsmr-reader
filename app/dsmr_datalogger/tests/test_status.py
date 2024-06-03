from django.test import TestCase, override_settings
from django.utils import timezone

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_datalogger.apps import check_recent_readings
from dsmr_datalogger.models.reading import DsmrReading


class TestStatus(TestCase):
    def setUp(self):
        DsmrReading.objects.create(
            timestamp=timezone.now() - timezone.timedelta(minutes=5),
            electricity_delivered_1=1,
            electricity_returned_1=0,
            electricity_delivered_2=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )
        self.assertEqual(DsmrReading.objects.count(), 1)

    @override_settings(DSMRREADER_STATUS_READING_OFFSET_MINUTES=6)
    def test_check_recent_readings_okay(self):
        self.assertIsNone(check_recent_readings())

    @override_settings(DSMRREADER_STATUS_READING_OFFSET_MINUTES=4)
    def test_check_recent_readings_fail(self):
        self.assertIsInstance(check_recent_readings(), MonitoringStatusIssue)

    def test_check_recent_readings_no_data(self):
        DsmrReading.objects.all().delete()
        self.assertEqual(DsmrReading.objects.count(), 0)
        self.assertIsInstance(check_recent_readings(), MonitoringStatusIssue)
