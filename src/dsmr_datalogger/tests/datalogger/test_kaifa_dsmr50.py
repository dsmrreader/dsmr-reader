from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from zoneinfo import ZoneInfo

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDatalogger(FakeDsmrReadingMixin, InterceptCommandStdoutMixin, TestCase):
    """Kaifa DSMR v5.0, with gas."""

    def _dsmr_dummy_data(self):
        return [
            "/KFM5KAIFA-METER\r\n",
            "\r\n",
            "1-3:0.2.8(50)\r\n",
            "0-0:1.0.0(261102203938W)\r\n",
            "0-0:96.1.1(4530303030303030303030303030303030)\r\n",
            "1-0:1.8.1(000001.140*kWh)\r\n",
            "1-0:1.8.2(000002.643*kWh)\r\n",
            "1-0:2.8.1(000000.000*kWh)\r\n",
            "1-0:2.8.2(000000.000*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.320*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00001)\r\n",
            "0-0:96.7.9(00000)\r\n",
            "1-0:99.97.0(0)(0-0:96.7.19)\r\n",
            "1-0:32.32.0(00000)\r\n",
            "1-0:52.32.0(00000)\r\n",
            "1-0:72.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "1-0:52.36.0(00000)\r\n",
            "1-0:72.36.0(00000)\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:32.7.0(229.0*V)\r\n",
            "1-0:52.7.0(231.0*V)\r\n",
            "1-0:72.7.0(232.0*V)\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:51.7.0(001*A)\r\n",
            "1-0:71.7.0(000*A)\r\n",
            "1-0:21.7.0(00.057*kW)\r\n",
            "1-0:41.7.0(00.263*kW)\r\n",
            "1-0:61.7.0(00.000*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "1-0:42.7.0(00.000*kW)\r\n",
            "1-0:62.7.0(00.000*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(4730303030303030303030303030303030)\r\n",
            "0-1:24.2.1(261102203500W)(00000.044*m3)\r\n",
            "!49A7\n",
        ]

    def test_reading_creation(self):
        """Test whether dsmr_datalogger can insert a reading for Kaifa DSMR v5.0."""
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_values(self):
        """Test whether dsmr_datalogger reads the correct values."""
        DataloggerSettings.get_solo()

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(reading.timestamp, datetime(2026, 11, 2, 19, 39, 38, tzinfo=ZoneInfo("UTC")))
        self.assertEqual(reading.electricity_delivered_1, Decimal("1.140"))
        self.assertEqual(reading.electricity_returned_1, Decimal("0"))
        self.assertEqual(reading.electricity_delivered_2, Decimal("2.643"))
        self.assertEqual(reading.electricity_returned_2, Decimal("0"))
        self.assertEqual(reading.electricity_currently_delivered, Decimal("0.320"))
        self.assertEqual(reading.electricity_currently_returned, Decimal("0"))
        self.assertEqual(reading.extra_device_timestamp, datetime(2026, 11, 2, 19, 35, tzinfo=ZoneInfo("UTC")))
        self.assertEqual(reading.extra_device_delivered, Decimal("0.044"))
        self.assertEqual(reading.phase_currently_delivered_l1, Decimal("0.057"))
        self.assertEqual(reading.phase_currently_delivered_l2, Decimal("0.263"))
        self.assertEqual(reading.phase_currently_delivered_l3, Decimal("0"))
        self.assertEqual(reading.phase_currently_returned_l1, Decimal("0"))
        self.assertEqual(reading.phase_currently_returned_l2, Decimal("0"))
        self.assertEqual(reading.phase_currently_returned_l3, Decimal("0"))
        self.assertEqual(reading.phase_voltage_l1, Decimal("229.0"))
        self.assertEqual(reading.phase_voltage_l2, Decimal("231.0"))
        self.assertEqual(reading.phase_voltage_l3, Decimal("232.0"))
        self.assertEqual(reading.phase_power_current_l1, 0)
        self.assertEqual(reading.phase_power_current_l2, 1)
        self.assertEqual(reading.phase_power_current_l3, 0)

        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, "50")
        self.assertEqual(meter_statistics.electricity_tariff, 2)
        self.assertEqual(meter_statistics.power_failure_count, 1)
        self.assertEqual(meter_statistics.long_power_failure_count, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, 0)
