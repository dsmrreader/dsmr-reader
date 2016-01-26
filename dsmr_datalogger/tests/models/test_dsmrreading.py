from django.test import TestCase

from dsmr_datalogger.models.reading import DsmrReading


class TestDsmrReading(TestCase):
    def test_ordering(self):
        """ Test whether default model sorting is as expected. """
        self.assertEqual(DsmrReading()._meta.ordering, ['timestamp'])
