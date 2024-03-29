from datetime import datetime
from decimal import Decimal

from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDatalogger(FakeDsmrReadingMixin, InterceptCommandStdoutMixin, TestCase):
    """Landis+Gyr 350 DSMR v4.0."""

    def _dsmr_dummy_data(self):
        return [
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(40)\r\n",
            "0-0:1.0.0(150701192959S)\r\n",
            "0-0:96.1.1(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)\r\n",
            "1-0:1.8.1(000510.747*kWh)\r\n",
            "1-0:2.8.1(000000.123*kWh)\r\n",
            "1-0:1.8.2(000500.013*kWh)\r\n",
            "1-0:2.8.2(000123.456*kWh)\r\n",
            "0-0:96.14.0(0001)\r\n",
            "1-0:1.7.0(00.192*kW)\r\n",
            "1-0:2.7.0(00.123*kW)\r\n",
            "0-0:17.0.0(999.9*kW)\r\n",
            "0-0:96.3.10(1)\r\n",
            "0-0:96.7.21(00003)\r\n",
            "0-0:96.7.9(00000)\r\n",
            "1-0:99.97.0(0)(0-0:96.7.19)\r\n",
            "1-0:32.32.0(00002)\r\n",
            "1-0:52.32.0(00002)\r\n",
            "1-0:72.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "1-0:52.36.0(00000)\r\n",
            "1-0:72.36.0(00000)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:51.7.0(000*A)\r\n",
            "1-0:71.7.0(001*A)\r\n",
            "1-0:21.7.0(00.123*kW)\r\n",
            "1-0:41.7.0(00.456*kW)\r\n",
            "1-0:61.7.0(00.789*kW)\r\n",
            "1-0:22.7.0(00.111*kW)\r\n",
            "1-0:42.7.0(00.555*kW)\r\n",
            "1-0:62.7.0(00.999*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)\r\n",
            "0-1:24.2.1(150701190000s)(00845.206*m3)\r\n",
            "0-1:24.4.0(1)\r\n",
            "!3F13\n",
        ]

    def test_reading_creation(self):
        """Test whether dsmr_datalogger can insert a reading for Landis+Gyr 350 DSMR v4.0."""
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_values(self):
        """Test whether dsmr_datalogger reads the correct values."""
        DataloggerSettings.get_solo()

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp, datetime(2015, 7, 1, 17, 29, 59, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal("510.747"))
        self.assertEqual(reading.electricity_returned_1, Decimal("0.123"))
        self.assertEqual(reading.electricity_delivered_2, Decimal("500.013"))
        self.assertEqual(reading.electricity_returned_2, Decimal("123.456"))
        self.assertEqual(reading.electricity_currently_delivered, Decimal("0.192"))
        self.assertEqual(reading.electricity_currently_returned, Decimal("0.123"))
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2015, 7, 1, 17, 0, 0, tzinfo=pytz.UTC),
        )
        self.assertEqual(reading.extra_device_delivered, Decimal("845.206"))
        self.assertEqual(reading.phase_currently_delivered_l1, Decimal("0.123"))
        self.assertEqual(reading.phase_currently_delivered_l2, Decimal("0.456"))
        self.assertEqual(reading.phase_currently_delivered_l3, Decimal("0.789"))
        self.assertEqual(reading.phase_currently_returned_l1, Decimal("0.111"))
        self.assertEqual(reading.phase_currently_returned_l2, Decimal("0.555"))
        self.assertEqual(reading.phase_currently_returned_l3, Decimal("0.999"))
        self.assertIsNone(reading.phase_voltage_l1)
        self.assertIsNone(reading.phase_voltage_l2)
        self.assertIsNone(reading.phase_voltage_l3)
        self.assertEqual(reading.phase_power_current_l1, 0)
        self.assertEqual(reading.phase_power_current_l2, 0)
        self.assertEqual(reading.phase_power_current_l3, 1)

        # Different data source.
        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, "40")
        self.assertEqual(meter_statistics.electricity_tariff, Decimal("1"))
        self.assertEqual(meter_statistics.power_failure_count, 3)
        self.assertEqual(meter_statistics.long_power_failure_count, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, 0)
