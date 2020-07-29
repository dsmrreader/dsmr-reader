from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.settings import RetentionSettings
import dsmr_datalogger.services.retention


class TestRetention(TestCase):
    fixtures = [
        'dsmr_datalogger/dsmrreading.json',
        'dsmr_datalogger/electricity-consumption.json',
        'dsmr_datalogger/gas-consumption.json',
    ]
    schedule_process = None

    def setUp(self):
        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_RETENTION_DATA_ROTATION)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

        RetentionSettings.get_solo()
        RetentionSettings.objects.update(data_retention_in_hours=None)  # Legacy tests: This used to be the default.
        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

    @mock.patch('django.utils.timezone.now')
    def test_disabled(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

        # Disabled settings should disable the process too.
        self.schedule_process.refresh_from_db()
        self.assertFalse(self.schedule_process.active)

    @mock.patch('django.utils.timezone.now')
    def test_enabled_with_cleanup(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        # Retention active, but point of retention not yet passed.
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_YEAR)
        RetentionSettings.get_solo().save()  # Trigger hook, faking interface action.

        dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

        # Allow point of retention to pass.
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_WEEK)
        RetentionSettings.get_solo().save()  # Trigger hook, faking interface action.

        # Should affect data now.
        dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.count(), 2)
        self.assertEqual(ElectricityConsumption.objects.count(), 8)
        self.assertEqual(GasConsumption.objects.count(), 32)

        # Make sure that specific data is kept.
        for x in [5629376, 5629427]:
            self.assertTrue(DsmrReading.objects.filter(pk=x).exists())

        for x in [95, 154, 155, 214, 215, 216, 217, 218]:
            self.assertTrue(ElectricityConsumption.objects.filter(pk=x).exists())

        self.assertFalse(GasConsumption.objects.filter(pk=32).exists())

        # As long as there was data, it should still be planned.
        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now())

    @mock.patch('django.utils.timezone.now')
    def test_enabled_no_cleanup(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        # Clean.
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_WEEK)
        dsmr_datalogger.services.retention.run(self.schedule_process)

        # No effect calling multiple times.
        dsmr_datalogger.services.retention.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.count(), 2)
        self.assertEqual(ElectricityConsumption.objects.count(), 8)
        self.assertEqual(GasConsumption.objects.count(), 32)

        # Should be delayed for a few hours now, nothing to do.
        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=12))
