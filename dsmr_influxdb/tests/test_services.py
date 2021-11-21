from decimal import Decimal
from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone
from influxdb_client import InfluxDBClient

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_influxdb.models import InfluxdbIntegrationSettings, InfluxdbMeasurement
import dsmr_influxdb.services


class TestCases(InterceptCommandStdoutMixin, TestCase):
    fixtures = ['dsmr_influxdb/measurements.json']

    def setUp(self):
        InfluxdbIntegrationSettings.get_solo()
        InfluxdbIntegrationSettings.objects.update(enabled=True)

        self.reading = DsmrReading.objects.create(
            timestamp=timezone.now(),
            electricity_delivered_1=1,
            electricity_returned_1=2,
            electricity_delivered_2=3,
            electricity_returned_2=4,
            electricity_currently_delivered=Decimal('1.234'),
            electricity_currently_returned=Decimal('5.6789'),
        )

    def test_initialize_client_disabled(self):
        InfluxdbIntegrationSettings.objects.update(enabled=False)

        client = dsmr_influxdb.services.initialize_client()
        self.assertIsNone(client)

    @mock.patch('influxdb_client.client.bucket_api.BucketsApi.find_bucket_by_name')
    @mock.patch('influxdb_client.client.bucket_api.BucketsApi.create_bucket')
    def test_initialize_client_connection_error(self, create_bucket_mock, find_bucket_mock):
        find_bucket_mock.return_value = None
        create_bucket_mock.side_effect = RuntimeError('Connection failed')

        with self.assertRaises(RuntimeError):
            dsmr_influxdb.services.initialize_client()

    @mock.patch('influxdb_client.client.bucket_api.BucketsApi.find_bucket_by_name')
    @mock.patch('influxdb_client.client.bucket_api.BucketsApi.create_bucket')
    def test_initialize_client_default(self, create_bucket_mock, find_bucket_mock):
        find_bucket_mock.return_value = None
        self.assertFalse(create_bucket_mock.called)

        client = dsmr_influxdb.services.initialize_client()
        self.assertIsNotNone(client)
        self.assertTrue(create_bucket_mock.called)
        self.assertTrue(client.url.startswith('http://'))

    @mock.patch('influxdb_client.client.bucket_api.BucketsApi.find_bucket_by_name')
    @mock.patch('influxdb_client.client.bucket_api.BucketsApi.create_bucket')
    def test_initialize_client_secure_unverified(self, create_bucket_mock, find_bucket_mock):
        find_bucket_mock.return_value = None
        InfluxdbIntegrationSettings.objects.update(secure=InfluxdbIntegrationSettings.SECURE_CERT_NONE)
        self.assertFalse(create_bucket_mock.called)

        client = dsmr_influxdb.services.initialize_client()
        self.assertIsNotNone(client)
        self.assertTrue(create_bucket_mock.called)
        self.assertTrue(client.url.startswith('https://'))

    @mock.patch('influxdb_client.client.bucket_api.BucketsApi.find_bucket_by_name')
    @mock.patch('influxdb_client.client.bucket_api.BucketsApi.create_bucket')
    def test_initialize_client_secure_verify_ssl(self, create_bucket_mock, find_bucket_mock):
        find_bucket_mock.return_value = None
        InfluxdbIntegrationSettings.objects.update(secure=InfluxdbIntegrationSettings.SECURE_CERT_REQUIRED)
        self.assertFalse(create_bucket_mock.called)

        client = dsmr_influxdb.services.initialize_client()
        self.assertIsNotNone(client)
        self.assertTrue(create_bucket_mock.called)
        self.assertTrue(client.url.startswith('https://'))

    @mock.patch('influxdb_client.client.write_api.WriteApi.write')
    def test_run_empty(self, write_points_mock):
        InfluxdbMeasurement.objects.all().delete()

        dsmr_influxdb.services.run(InfluxDBClient('http://localhost:8086', ''))
        self.assertFalse(write_points_mock.called)  # Not reached.

    @mock.patch('influxdb_client.client.write_api.WriteApi.write')
    def test_run_exception(self, write_points_mock):
        write_points_mock.side_effect = RuntimeError('Explosion')

        dsmr_influxdb.services.run(InfluxDBClient('http://localhost:8086', ''))

        # No crash and should still clear data.
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)

    @mock.patch('influxdb_client.client.write_api.WriteApi.write')
    def test_run(self, write_points_mock):
        self.assertFalse(write_points_mock.called)
        self.assertEqual(InfluxdbMeasurement.objects.count(), 3)

        dsmr_influxdb.services.run(InfluxDBClient('http://localhost:8086', ''))
        self.assertTrue(write_points_mock.called)
        self.assertEqual(write_points_mock.call_count, 3)
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)

    @override_settings(DSMRREADER_INFLUXDB_MAX_MEASUREMENTS_IN_QUEUE=1)
    @mock.patch('influxdb_client.client.write_api.WriteApi.write')
    def test_run_overrun(self, write_points_mock):
        """ More measurements stored than we're allowed to process. """
        self.assertFalse(write_points_mock.called)
        self.assertEqual(InfluxdbMeasurement.objects.count(), 3)

        dsmr_influxdb.services.run(InfluxDBClient('http://localhost:8086', ''))

        self.assertTrue(write_points_mock.called)
        self.assertEqual(write_points_mock.call_count, 1)  # Only once
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)

    def test_publish_dsmr_reading_disabled(self):
        InfluxdbIntegrationSettings.objects.update(enabled=False)

        InfluxdbMeasurement.objects.all().delete()
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)

        dsmr_influxdb.services.publish_dsmr_reading(self.reading)

        # Still nothing, because it's blocked.
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)

    def test_publish_dsmr_reading(self):
        InfluxdbMeasurement.objects.all().delete()
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)

        dsmr_influxdb.services.publish_dsmr_reading(self.reading)

        # Assumes default mapping.
        self.assertEqual(InfluxdbMeasurement.objects.count(), 6)
        self.assertTrue(InfluxdbMeasurement.objects.filter(measurement_name='electricity_live').exists())
        self.assertTrue(InfluxdbMeasurement.objects.filter(measurement_name='electricity_positions').exists())
        self.assertTrue(InfluxdbMeasurement.objects.filter(measurement_name='electricity_voltage').exists())
        self.assertTrue(InfluxdbMeasurement.objects.filter(measurement_name='electricity_phases').exists())
        self.assertTrue(InfluxdbMeasurement.objects.filter(measurement_name='electricity_power').exists())
        self.assertTrue(InfluxdbMeasurement.objects.filter(measurement_name='gas_positions').exists())

    @mock.patch('logging.Logger.warning')
    def test_publish_dsmr_reading_invalid_mapping(self, warning_logger_mock):
        InfluxdbIntegrationSettings.objects.update(formatting="""
[fake]
non_existing_field = whatever
""")

        InfluxdbMeasurement.objects.all().delete()
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)

        dsmr_influxdb.services.publish_dsmr_reading(self.reading)

        # Invalid mapping.
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)
        self.assertFalse(InfluxdbMeasurement.objects.filter(measurement_name='fake').exists())
        self.assertTrue(warning_logger_mock.callled)
