from django.test import TestCase, override_settings
from django.utils import timezone

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_consumption.apps import check_unprocessed_readings
from dsmr_datalogger.models.reading import DsmrReading


class TestStatus(TestCase):
    def setUp(self):
        DsmrReading.objects.create(
            timestamp=timezone.now(),
            electricity_delivered_1=1,
            electricity_returned_1=0,
            electricity_delivered_2=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )
        self.assertEqual(DsmrReading.objects.unprocessed().count(), 1)

    @override_settings(DSMRREADER_STATUS_MAX_UNPROCESSED_READINGS=1)
    def test_check_unprocessed_readings_okay(self):
        self.assertIsNone(check_unprocessed_readings())

    @override_settings(DSMRREADER_STATUS_MAX_UNPROCESSED_READINGS=0)
    def test_check_unprocessed_readings_fail(self):
        self.assertIsInstance(check_unprocessed_readings(), MonitoringStatusIssue)
