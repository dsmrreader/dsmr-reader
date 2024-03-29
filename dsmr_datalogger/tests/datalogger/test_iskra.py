from unittest import mock
from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
import pytz

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDatalogger(FakeDsmrReadingMixin, InterceptCommandStdoutMixin, TestCase):
    """Iskra meter, unknown DSMR version, asumed v2/3."""

    def setUp(self):
        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.dsmr_version = DataloggerSettings.DSMR_VERSION_2_3
        datalogger_settings.save()

    def _dsmr_dummy_data(self):
        return [
            "/ISk5\2MT382-1003\r\n",
            "\r\n",
            "0-0:96.1.1(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)\r\n",
            "1-0:1.8.1(01234.784*kWh)\r\n",
            "1-0:1.8.2(04321.725*kWh)\r\n",
            "1-0:2.8.1(00000.000*kWh)\r\n",
            "1-0:2.8.2(00000.002*kWh)\r\n",
            "0-0:96.14.0(0001)\r\n",
            "1-0:1.7.0(0000.36*kW)\r\n",
            "1-0:2.7.0(0000.00*kW)\r\n",
            "0-0:17.0.0(0999.00*kW)\r\n",
            "0-0:96.3.10(1)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "0-1:24.1.0(3)\r\n",
            "0-1:96.1.0(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)\r\n",
            "0-1:24.3.0(160410130000)(2C)(60)(1)(0-1:24.2.1)(m3)\r\n",
            "(07890.693)\r\n",
            "0-1:24.4.0(1)\r\n",
            "!",
        ]

    def test_reading_creation(self):
        """Test whether dsmr_datalogger can insert a reading."""
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    @mock.patch("django.utils.timezone.now")
    def test_reading_values(self, now_mock):
        """Test whether dsmr_datalogger reads the correct values."""
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 4, 10, hour=14, minute=30, second=15)
        )

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp, datetime(2016, 4, 10, 12, 30, 15, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal("1234.784"))
        self.assertEqual(reading.electricity_returned_1, Decimal("0"))
        self.assertEqual(reading.electricity_delivered_2, Decimal("4321.725"))
        self.assertEqual(reading.electricity_returned_2, Decimal("0.002"))
        self.assertEqual(reading.electricity_currently_delivered, Decimal("0.36"))
        self.assertEqual(reading.electricity_currently_returned, Decimal("0"))
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2016, 4, 10, 11, 0, 0, tzinfo=pytz.UTC),
        )
        self.assertEqual(reading.extra_device_delivered, Decimal("7890.693"))
        self.assertIsNone(reading.phase_voltage_l1)
        self.assertIsNone(reading.phase_voltage_l2)
        self.assertIsNone(reading.phase_voltage_l3)
        self.assertIsNone(reading.phase_power_current_l1)
        self.assertIsNone(reading.phase_power_current_l2)
        self.assertIsNone(reading.phase_power_current_l3)

        meter_statistics = MeterStatistics.get_solo()
        self.assertIsNone(meter_statistics.dsmr_version)
        self.assertEqual(meter_statistics.electricity_tariff, 1)
        self.assertEqual(meter_statistics.power_failure_count, None)
        self.assertEqual(meter_statistics.long_power_failure_count, None)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, None)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, None)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, None)

    @mock.patch("django.utils.timezone.now")
    def test_telegram_override_timestamp(self, now_mock):
        """Tests whether this user setting overrides as expectedly."""
        reading = self._reading_with_override_telegram_timestamp_active(now_mock)

        self.assertEqual(
            # CET > UTC. Minute marker rounded to hours. Because Fluvius may or may not communicate DSMR v5 in telegrams
            reading.extra_device_timestamp,
            datetime(2021, 1, 15, 11, 0, 0, 0, tzinfo=pytz.UTC),
        )
