from django.core.management import call_command, CommandError
from django.test import TestCase
from django.utils import timezone

from dsmr_stats.models import DsmrReading, ElectricityConsumption, GasConsumption,\
    ElectricityStatistics


class TestDsmrStatsCompactor(TestCase):
    """ Test 'dsmr_stats_compactor' management command. """
    fixtures = ['test_dsmrreading.json']

    def setUp(self):
        self.assertEqual(DsmrReading.objects.all().count(), 3)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())

    def test_processing(self):
        call_command('dsmr_stats_compactor')

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 3)
        self.assertEqual(GasConsumption.objects.count(), 1)

    def test_grouping(self):
        # Make sure to verify the blocking of read ahead.
        dr = DsmrReading.objects.get(pk=3)
        dr.timestamp = timezone.now()
        dr.save()

        call_command('dsmr_stats_compactor', group_by_minute=True)

        self.assertEqual(DsmrReading.objects.unprocessed().count(), 1)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 1)
        self.assertEqual(GasConsumption.objects.count(), 1)

    def test_creation(self):
        self.assertFalse(ElectricityStatistics.objects.exists())
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())

        call_command('dsmr_stats_compactor')

        self.assertTrue(ElectricityStatistics.objects.exists())
        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())

    def test_purge(self):
        call_command('dsmr_stats_compactor')
        self.assertTrue(ElectricityStatistics.objects.exists())
        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())

        with self.assertRaises(CommandError):
            call_command('dsmr_stats_compactor', purge=True)

        self.assertFalse(ElectricityStatistics.objects.exists())
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
