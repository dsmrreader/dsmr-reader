from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone
from influxdb import InfluxDBClient

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_influxdb.models import InfluxdbIntegrationSettings, InfluxdbMeasurement
import dsmr_influxdb.services


class TestCases(InterceptStdoutMixin, TestCase):
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
            electricity_currently_delivered=5,
            electricity_currently_returned=6,
        )

    def test_initialize_client_disabled(self):
        InfluxdbIntegrationSettings.objects.update(enabled=False)

        client = dsmr_influxdb.services.initialize_client()
        self.assertIsNone(client)

    @mock.patch('influxdb.InfluxDBClient.create_database')
    def test_initialize_client_default(self, create_database_mock):
        self.assertFalse(create_database_mock.called)
        client = dsmr_influxdb.services.initialize_client()
        self.assertTrue(create_database_mock.called)
        self.assertIsNotNone(client)
        self.assertEqual(client._scheme, 'http')
        self.assertFalse(client._verify_ssl)

    @mock.patch('influxdb.InfluxDBClient.create_database')
    def test_initialize_client_secure_unverified(self, create_database_mock):
        InfluxdbIntegrationSettings.objects.update(secure=InfluxdbIntegrationSettings.SECURE_CERT_NONE)

        self.assertFalse(create_database_mock.called)
        client = dsmr_influxdb.services.initialize_client()
        self.assertIsNotNone(client)

        self.assertEqual(client._scheme, 'https')
        self.assertFalse(client._verify_ssl)

    @mock.patch('influxdb.InfluxDBClient.create_database')
    def test_initialize_client_secure_verify_ssl(self, create_database_mock):
        InfluxdbIntegrationSettings.objects.update(secure=InfluxdbIntegrationSettings.SECURE_CERT_REQUIRED)

        self.assertFalse(create_database_mock.called)
        client = dsmr_influxdb.services.initialize_client()
        self.assertIsNotNone(client)

        self.assertEqual(client._scheme, 'https')
        self.assertTrue(client._verify_ssl)

    @mock.patch('influxdb.InfluxDBClient.write_points')
    def test_run_empty(self, write_points_mock):
        InfluxdbMeasurement.objects.all().delete()

        dsmr_influxdb.services.run(InfluxDBClient())
        self.assertFalse(write_points_mock.called)  # Not reached.

    @mock.patch('influxdb.InfluxDBClient.write_points')
    def test_run(self, write_points_mock):
        self.assertFalse(write_points_mock.called)
        self.assertEqual(InfluxdbMeasurement.objects.count(), 3)

        dsmr_influxdb.services.run(InfluxDBClient())
        self.assertTrue(write_points_mock.called)
        self.assertEqual(write_points_mock.call_count, 1)
        self.assertEqual(InfluxdbMeasurement.objects.count(), 0)

    @override_settings(DSMRREADER_INFLUXDB_MAX_MESSAGES_IN_QUEUE=1)
    @mock.patch('influxdb.InfluxDBClient.write_points')
    def test_run_overrun(self, write_points_mock):
        """ More measurements stored than we're allowed to process. """
        self.assertFalse(write_points_mock.called)
        self.assertEqual(InfluxdbMeasurement.objects.count(), 3)

        dsmr_influxdb.services.run(InfluxDBClient())

        self.assertTrue(write_points_mock.called)
        self.assertEqual(write_points_mock.call_count, 1)
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
