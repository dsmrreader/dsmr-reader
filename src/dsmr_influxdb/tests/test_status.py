from django.test import TestCase, override_settings
from django.utils import timezone

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_influxdb.apps import check_influxdb_measurements_queue
from dsmr_influxdb.models import InfluxdbMeasurement


class TestStatus(TestCase):
    def setUp(self):
        InfluxdbMeasurement.objects.create(
            time=timezone.now(),
            measurement_name="test",
            fields="[]",
        )
        self.assertEqual(InfluxdbMeasurement.objects.all().count(), 1)

    @override_settings(DSMRREADER_INFLUXDB_MAX_MEASUREMENTS_IN_QUEUE=2)
    def test_check_influxdb_measurements_queue_okay(self):
        self.assertIsNone(check_influxdb_measurements_queue())

    @override_settings(DSMRREADER_INFLUXDB_MAX_MEASUREMENTS_IN_QUEUE=1)
    def test_check_influxdb_measurements_queue_fail(self):
        self.assertIsInstance(
            check_influxdb_measurements_queue(), MonitoringStatusIssue
        )
