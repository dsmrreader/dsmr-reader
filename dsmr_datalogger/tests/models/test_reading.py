from django.test import TestCase
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics


class TestDsmrReading(TestCase):
    def setUp(self):
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


class TestMeterStatistics(TestCase):
    def setUp(self):
        self.instance = MeterStatistics.get_solo()

    def test_ordering(self):
        """ Test whether defaults allow the creation of any empty model. """
        MeterStatistics.get_solo()
        self.assertTrue(MeterStatistics.objects.exists())

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'MeterStatistics')
