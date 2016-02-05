from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.settings import ConsumptionSettings


class TestDsmrStatsCompactor(CallCommandStdoutMixin, TestCase):
    """ Test 'dsmr_backend' management command. """
    fixtures = ['dsmr_consumption/test_dsmrreading.json']

    def setUp(self):
        self.assertEqual(DsmrReading.objects.all().count(), 3)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())

        # Initializes singleton model.
        ConsumptionSettings.get_solo()

    def test_processing(self):
        """ Test fixed data parse outcome. """
        # Default is grouping by minute, so make sure to revert that here.
        consumption_settings = ConsumptionSettings.get_solo()
        consumption_settings.compactor_grouping_type = ConsumptionSettings.COMPACTOR_GROUPING_BY_READING
        consumption_settings.save()

        self._call_command_stdout('dsmr_backend')

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 3)
        self.assertEqual(GasConsumption.objects.count(), 1)

    @mock.patch('dsmr_consumption.signals.gas_consumption_created.send_robust')
    def test_consumption_creation_signal(self, signal_mock):
        """ Test outgoing signal communication. """
        self.assertFalse(signal_mock.called)
        self._call_command_stdout('dsmr_backend')
        self.assertTrue(signal_mock.called)

    def test_grouping(self):
        """ Test grouping per minute, instead of the default 10-second interval. """
        # Make sure to verify the blocking of read ahead.
        dr = DsmrReading.objects.get(pk=3)
        dr.timestamp = timezone.now()
        dr.save()

        self._call_command_stdout('dsmr_backend')

        self.assertEqual(DsmrReading.objects.unprocessed().count(), 1)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 1)
        self.assertEqual(GasConsumption.objects.count(), 1)

    def test_creation(self):
        """ Test the datalogger's builtin fallback for initial readings. """
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())

        self._call_command_stdout('dsmr_backend')

        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())
