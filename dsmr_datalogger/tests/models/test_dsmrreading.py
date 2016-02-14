from django.test import TestCase

from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics


class TestDsmrReading(TestCase):
    def test_ordering(self):
        """ Test whether default model sorting is as expected. """
        self.assertEqual(DsmrReading()._meta.ordering, ['timestamp'])


class TestMeterStatistics(TestCase):
    def test_ordering(self):
        """ Test whether defaults allow the creation of any empty model. """
        MeterStatistics.get_solo()
        self.assertTrue(MeterStatistics.objects.exists())
