from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_influxdb.models import InfluxdbMeasurement


class TestCommand(InterceptCommandStdoutMixin, TestCase):
    def test_dsmr_mqtt_clear_queue(self):
        InfluxdbMeasurement.objects.create(
            time=timezone.now(), measurement_name="y", fields="z"
        )
        self.assertEqual(InfluxdbMeasurement.objects.all().count(), 1)

        self._intercept_command_stdout("dsmr_influxdb_clear_queue")

        self.assertEqual(InfluxdbMeasurement.objects.all().count(), 0)
