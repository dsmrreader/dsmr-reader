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
    """Belgium Fluvius meter (another sample)."""

    def setUp(self):
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(
            dsmr_version=DataloggerSettings.DSMR_BELGIUM_FLUVIUS
        )

    def _dsmr_dummy_data(self):
        return [
            "/FLU5\123456789_A\r\n",
            "\r\n",
            "0-0:96.1.4(50213)\r\n",
            "0-0:96.1.1(12345678901234567890123456789012)\r\n",
            "0-0:1.0.0(200807082711S)\r\n",
            "1-0:1.8.1(001924.771*kWh)\r\n",
            "1-0:1.8.2(002549.919*kWh)\r\n",
            "1-0:2.8.1(001968.710*kWh)\r\n",
            "1-0:2.8.2(000692.984*kWh)\r\n",
            "0-0:96.14.0(0001)\r\n",
            "1-0:1.7.0(00.000*kW)\r\n",
            "1-0:2.7.0(00.611*kW)\r\n",
            "1-0:32.7.0(235.6*V)\r\n",
            "1-0:31.7.0(002*A)\r\n",
            "0-0:96.3.10(1)\r\n",
            "0-0:17.0.0(999.9*kW)\r\n",
            "1-0:31.4.0(999*A)\r\n",
            "0-0:96.13.0()\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.1(12345678901234567890123456789012)\r\n",
            "0-1:24.4.0(1)\r\n",
            "0-1:24.2.3(200807082502S)(01414.287*m3)\r\n",
            "!81A9",
        ]

    def test_reading_creation(self):
        """Test whether dsmr_datalogger can insert a reading."""
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    @mock.patch("django.utils.timezone.now")
    def test_reading_values(self, now_mock):
        """Test whether dsmr_datalogger reads the correct values."""
        now_mock.return_value = timezone.make_aware(timezone.datetime(2021, 1, 1))
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp, datetime(2020, 8, 7, 6, 27, 11, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal("1924.771"))
        self.assertEqual(reading.electricity_returned_1, Decimal("1968.710"))
        self.assertEqual(reading.electricity_delivered_2, Decimal("2549.919"))
        self.assertEqual(reading.electricity_returned_2, Decimal("692.984"))
        self.assertEqual(reading.electricity_currently_delivered, Decimal("0"))
        self.assertEqual(reading.electricity_currently_returned, Decimal("0.611"))
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2020, 8, 7, 6, 25, 2, tzinfo=pytz.UTC),
        )
        self.assertEqual(reading.extra_device_delivered, Decimal("1414.287"))
        self.assertEqual(reading.phase_voltage_l1, Decimal("235.6"))
        self.assertEqual(reading.phase_voltage_l2, None)
        self.assertEqual(reading.phase_voltage_l3, None)
        self.assertEqual(reading.phase_power_current_l1, 2)
        self.assertEqual(reading.phase_power_current_l2, None)
        self.assertEqual(reading.phase_power_current_l3, None)

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
