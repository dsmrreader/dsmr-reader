from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading


class TestDsmrReading(TestCase):
    @mock.patch('django.utils.timezone.now')
    def setUp(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1), timezone=timezone.utc)
        self.instance = DsmrReading.objects.create(
            timestamp=timezone.now(),
            electricity_delivered_1=1,
            electricity_returned_1=2,
            electricity_delivered_2=3,
            electricity_returned_2=4,
            electricity_currently_delivered=5,
            electricity_currently_returned=6,
        )

    def test_ordering(self):
        """ Test whether default model sorting is as expected. """
        self.assertEqual(DsmrReading()._meta.ordering, ['timestamp'])

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'DsmrReading')

    def test_managers(self):
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        DsmrReading.objects.all().update(processed=True)
        self.assertTrue(DsmrReading.objects.processed().exists())

    @mock.patch('django.utils.timezone.now')
    def test_convert_to_local_timezone(self, now_mock):
        """ Test altering the timezone formatting for the timestamps. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1), timezone=timezone.utc)

        self.assertEqual(str(self.instance.timestamp), '2018-01-01 00:00:00+00:00')
        self.assertIsNone(self.instance.extra_device_timestamp)

        # Only timestamp.
        self.instance.convert_to_local_timezone()
        self.assertEqual(str(self.instance.timestamp), '2018-01-01 01:00:00+01:00')
        self.assertIsNone(self.instance.extra_device_timestamp)

        # Now extra device.
        self.instance.extra_device_timestamp = timezone.now() + timezone.timedelta(hours=12)
        self.assertEqual(str(self.instance.extra_device_timestamp), '2018-01-01 12:00:00+00:00')

        # Both.
        self.instance.convert_to_local_timezone()
        self.assertEqual(str(self.instance.timestamp), '2018-01-01 01:00:00+01:00')
        self.assertEqual(str(self.instance.extra_device_timestamp), '2018-01-01 13:00:00+01:00')
