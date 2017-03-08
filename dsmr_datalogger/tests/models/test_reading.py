from django.test import TestCase
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics


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

    def test_managers(self):
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        DsmrReading.objects.all().update(processed=True)
        self.assertTrue(DsmrReading.objects.processed().exists())


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
