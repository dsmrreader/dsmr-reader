import warnings
from unittest import mock

from django.core.management import CommandError
from django.test import TestCase
from django.utils import timezone

from dsmr_stats.tests.mixins import CallCommandStdoutMixin
from dsmr_stats.models.reading import DsmrReading
from dsmr_stats.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.models.statistics import ElectricityStatistics
from dsmr_stats.models.settings import StatsSettings


class TestDsmrStatsCompactor(CallCommandStdoutMixin, TestCase):
    """ Test 'dsmr_stats_compactor' management command. """
    fixtures = ['dsmr_stats/test_dsmrreading.json']

    def setUp(self):
        self.assertEqual(DsmrReading.objects.all().count(), 3)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())

        # Initializes singleton model.
        StatsSettings.get_solo()

    def test_processing(self):
        """ Test fixed data parse outcome. """
        # Default is grouping by minute, so make sure to revert that here.
        stats_settings = StatsSettings.get_solo()
        stats_settings.compactor_grouping_type = StatsSettings.COMPACTOR_GROUPING_BY_READING
        stats_settings.save()

        self._call_command_stdout('dsmr_stats_compactor')

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 3)
        self.assertEqual(GasConsumption.objects.count(), 1)

    @mock.patch('dsmrreader.signals.gas_consumption_created.send_robust')
    def test_consumption_creation_signal(self, signal_mock):
        """ Test outgoing signal communication. """
        self.assertFalse(signal_mock.called)
        self._call_command_stdout('dsmr_stats_compactor')
        self.assertTrue(signal_mock.called)

    def test_grouping(self):
        """ Test grouping per minute, instead of the default 10-second interval. """
        # Make sure to verify the blocking of read ahead.
        dr = DsmrReading.objects.get(pk=3)
        dr.timestamp = timezone.now()
        dr.save()

        self._call_command_stdout('dsmr_stats_compactor')

        self.assertEqual(DsmrReading.objects.unprocessed().count(), 1)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 1)
        self.assertEqual(GasConsumption.objects.count(), 1)

    def test_deprecated_grouping_argument(self):
        """ Tests whether we raise an deprecation warning for using the grouping argument. """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                self._call_command_stdout('dsmr_stats_compactor', group_by_minute=True)
            except RuntimeError:
                pass

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertEqual(
                w[-1].message,
                'group_by_minute argument is DEPRECATED and moved to the database settings'
            )

    def test_creation(self):
        """ Test the datalogger's builtin fallback for initial readings. """
        self.assertFalse(ElectricityStatistics.objects.exists())
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())

        self._call_command_stdout('dsmr_stats_compactor')

        self.assertTrue(ElectricityStatistics.objects.exists())
        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())

    def test_purge(self):
        """ Test global consumption reset. """
        self._call_command_stdout('dsmr_stats_compactor')
        self.assertTrue(ElectricityStatistics.objects.exists())
        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())

        with self.assertRaises(CommandError):
            self._call_command_stdout('dsmr_stats_compactor', purge=True)

        self.assertFalse(ElectricityStatistics.objects.exists())
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
