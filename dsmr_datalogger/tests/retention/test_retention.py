from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.settings import RetentionSettings
from dsmr_backend.exceptions import DelayNextCall
import dsmr_datalogger.services


class TestRetention(TestCase):
    fixtures = [
        'dsmr_datalogger/dsmrreading.json',
        'dsmr_datalogger/electricity-consumption.json',
        'dsmr_datalogger/gas-consumption.json',
    ]

    @mock.patch('django.utils.timezone.now')
    def test_retention_timestamp_restrictions(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25, hour=12))

        RetentionSettings.get_solo()
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_WEEK)

        self.assertEqual(DsmrReading.objects.count(), 52)

        try:
            # Retention should do nothing, since it's noon.
            dsmr_datalogger.services.apply_data_retention()
        except DelayNextCall:
            pass

        self.assertEqual(DsmrReading.objects.count(), 52)

        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25, hour=5))
        self.assertEqual(DsmrReading.objects.count(), 52)

        try:
            # Retention should kick in now.
            dsmr_datalogger.services.apply_data_retention()
        except DelayNextCall:
            pass

        self.assertEqual(DsmrReading.objects.count(), 2)

    @mock.patch('django.utils.timezone.now')
    def test_apply_data_retention_fail(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

        try:
            # Default inactive.
            dsmr_datalogger.services.apply_data_retention()
        except DelayNextCall:
            pass

        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

        # Retention active, but point of retention not yet passed.
        RetentionSettings.get_solo()
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_YEAR)

        try:
            dsmr_datalogger.services.apply_data_retention()
        except DelayNextCall:
            pass

        self.assertEqual(DsmrReading.objects.count(), 52)
        self.assertEqual(ElectricityConsumption.objects.count(), 67)
        self.assertEqual(GasConsumption.objects.count(), 33)

    @mock.patch('django.utils.timezone.now')
    def test_apply_data_retention_okay(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 12, 25))

        # Allow point of retention to pass.
        RetentionSettings.get_solo()
        RetentionSettings.objects.update(data_retention_in_hours=RetentionSettings.RETENTION_WEEK)

        try:
            # Should affect data now.
            dsmr_datalogger.services.apply_data_retention()
        except DelayNextCall:
            pass

        self.assertEqual(DsmrReading.objects.count(), 2)
        self.assertEqual(ElectricityConsumption.objects.count(), 8)
        self.assertEqual(GasConsumption.objects.count(), 32)

        # Make sure that specific data is kept.
        for x in [5629376, 5629427]:
            self.assertTrue(DsmrReading.objects.filter(pk=x).exists())

        for x in [95, 154, 155, 214, 215, 216, 217, 218]:
            self.assertTrue(ElectricityConsumption.objects.filter(pk=x).exists())

        self.assertFalse(GasConsumption.objects.filter(pk=32).exists())

        try:
            # No effect calling multiple times.
            dsmr_datalogger.services.apply_data_retention()
        except DelayNextCall:
            pass

        self.assertEqual(DsmrReading.objects.count(), 2)
        self.assertEqual(ElectricityConsumption.objects.count(), 8)
        self.assertEqual(GasConsumption.objects.count(), 32)
