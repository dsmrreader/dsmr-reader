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
    """Belgium Fluvius meter with the late 2022 peak data field."""

    def setUp(self):
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(
            dsmr_version=DataloggerSettings.DSMR_BELGIUM_FLUVIUS
        )

    def _dsmr_dummy_data(self):
        return [
            "/FLU5\253769484_A\r\n",
            "\r\n",
            "0-0:96.1.4(50217)\r\n",
            "0-0:96.1.1(12345678901234567890123456789012)\r\n",
            "0-0:1.0.0(230201155056W)\r\n",
            "1-0:1.8.1(000143.608*kWh)\r\n",
            "1-0:1.8.2(000170.853*kWh)\r\n",
            "1-0:2.8.1(000002.963*kWh)\r\n",
            "1-0:2.8.2(000000.427*kWh)\r\n",
            "0-0:96.14.0(0001)\r\n",
            "1-0:1.4.0(00.078*kW)\r\n",
            "1-0:1.6.0(230201020000W)(01.566*kW)\r\n",
            "0-0:98.1.0(1)(1-0:1.6.0)(1-0:1.6.0)(230201000000W)(230114124500W)(03.332*kW)\r\n",
            "1-0:1.7.0(00.182*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "1-0:21.7.0(00.230*kW)\r\n",
            "1-0:41.7.0(00.000*kW)\r\n",
            "1-0:61.7.0(00.000*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "1-0:42.7.0(00.000*kW)\r\n",
            "1-0:62.7.0(00.048*kW)\r\n",
            "1-0:32.7.0(227.8*V)\r\n",
            "1-0:52.7.0(000.0*V)\r\n",
            "1-0:72.7.0(231.5*V)\r\n",
            "1-0:31.7.0(001.60*A)\r\n",
            "1-0:51.7.0(001.66*A)\r\n",
            "1-0:71.7.0(001.41*A)\r\n",
            "0-0:96.3.10(1)\r\n",
            "0-0:17.0.0(999.9*kW)\r\n",
            "1-0:31.4.0(999*A)\r\n",
            "0-0:96.13.0()\r\n",
            "!59A5",
        ]

    def test_reading_creation(self):
        """Test whether dsmr_datalogger can insert a reading."""
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    @mock.patch("django.utils.timezone.now")
    def test_reading_values(self, now_mock):
        """Test whether dsmr_datalogger reads the correct values."""
        now_mock.return_value = timezone.make_aware(timezone.datetime(2023, 2, 1))
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp, datetime(2023, 2, 1, 14, 50, 56, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal("143.608"))
        self.assertEqual(reading.electricity_returned_1, Decimal("2.963"))
        self.assertEqual(reading.electricity_delivered_2, Decimal("170.853"))
        self.assertEqual(reading.electricity_returned_2, Decimal("0.427"))
        self.assertEqual(reading.electricity_currently_delivered, Decimal("0.182"))
        self.assertEqual(reading.electricity_currently_returned, Decimal("0"))
        self.assertEqual(reading.extra_device_timestamp, None)  # Error handled.
        self.assertEqual(
            reading.extra_device_delivered, None
        )  # Should be NONE too due to timestamp.
        self.assertEqual(reading.phase_voltage_l1, Decimal("227.8"))
        self.assertEqual(reading.phase_voltage_l2, Decimal("0"))
        self.assertEqual(reading.phase_voltage_l3, Decimal("231.5"))
        self.assertEqual(reading.phase_power_current_l1, 1)
        self.assertEqual(reading.phase_power_current_l2, 1)
        self.assertEqual(reading.phase_power_current_l3, 1)

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
            reading.extra_device_delivered, None
        )  # Should be NONE too due to timestamp.
