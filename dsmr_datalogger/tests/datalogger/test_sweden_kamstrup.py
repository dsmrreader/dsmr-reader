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
    """Swedish Kamstrup meter. Compatible with Luxembourg meter."""

    def setUp(self):
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(
            dsmr_version=DataloggerSettings.DSMR_LUXEMBOURG_SMARTY
        )

    def _dsmr_dummy_data(self):
        return [
            "/KAM5\r\n",
            "\r\n",
            "0-0:1.0.0(211115100940W)\r\n",
            "1-0:1.8.0(00000003.997*kWh)\r\n",
            "1-0:2.8.0(00000000.000*kWh)\r\n",
            "1-0:3.8.0(00000000.000*kVArh)\r\n",
            "1-0:4.8.0(00000000.000*kVArh)\r\n",
            "1-0:1.7.0(0000.000*kW)\r\n",
            "1-0:2.7.0(0000.000*kW)\r\n",
            "1-0:3.7.0(0000.000*kVAr)\r\n",
            "1-0:4.7.0(0000.000*kVAr)\r\n",
            "1-0:21.7.0(0000.000*kW)\r\n",
            "1-0:41.7.0(0000.000*kW)\r\n",
            "1-0:61.7.0(0000.000*kW)\r\n",
            "1-0:22.7.0(0000.000*kW)\r\n",
            "1-0:42.7.0(0000.000*kW)\r\n",
            "1-0:62.7.0(0000.000*kW)\r\n",
            "1-0:23.7.0(0000.000*kVAr)\r\n",
            "1-0:43.7.0(0000.000*kVAr)\r\n",
            "1-0:63.7.0(0000.000*kVAr)\r\n",
            "1-0:24.7.0(0000.000*kVAr)\r\n",
            "1-0:44.7.0(0000.000*kVAr)\r\n",
            "1-0:64.7.0(0000.000*kVAr)\r\n",
            "1-0:32.7.0(238.0*V)\r\n",
            "1-0:52.7.0(238.0*V)\r\n",
            "1-0:72.7.0(240.7*V)\r\n",
            "1-0:31.7.0(000.0*A)\r\n",
            "1-0:51.7.0(000.0*A)\r\n",
            "1-0:71.7.0(000.0*A)\r\n",
            "!5FCE\n",
        ]

    def test_reading_creation(self):
        """Test whether dsmr_datalogger can insert a reading."""
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    @mock.patch("django.utils.timezone.now")
    def test_reading_values(self, now_mock):
        """Test whether dsmr_datalogger reads the correct values."""
        now_mock.return_value = timezone.make_aware(timezone.datetime(2021, 11, 15))
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp, datetime(2021, 11, 15, 9, 9, 40, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal("3.997"))
        self.assertEqual(reading.electricity_returned_1, Decimal("0"))
        self.assertEqual(reading.electricity_delivered_2, Decimal("0"))
        self.assertEqual(reading.electricity_returned_2, Decimal("0"))
        self.assertEqual(reading.electricity_currently_delivered, Decimal("0"))
        self.assertEqual(reading.electricity_currently_returned, Decimal("0"))
        self.assertIsNone(reading.extra_device_timestamp)
        self.assertIsNone(reading.extra_device_delivered)
        self.assertEqual(reading.phase_voltage_l1, Decimal("238.0"))
        self.assertEqual(reading.phase_voltage_l2, Decimal("238.0"))
        self.assertEqual(reading.phase_voltage_l3, Decimal("240.7"))
        self.assertEqual(reading.phase_power_current_l1, Decimal("0.0"))
        self.assertEqual(reading.phase_power_current_l2, Decimal("0.0"))
        self.assertEqual(reading.phase_power_current_l3, Decimal("0.0"))

        meter_statistics = MeterStatistics.get_solo()
        self.assertIsNone(meter_statistics.dsmr_version)
        self.assertIsNone(meter_statistics.electricity_tariff)
        self.assertIsNone(meter_statistics.power_failure_count)
        self.assertIsNone(meter_statistics.long_power_failure_count)
        self.assertIsNone(meter_statistics.voltage_sag_count_l1)
        self.assertIsNone(meter_statistics.voltage_sag_count_l2)
        self.assertIsNone(meter_statistics.voltage_sag_count_l3)
        self.assertIsNone(meter_statistics.voltage_swell_count_l1)
        self.assertIsNone(meter_statistics.voltage_swell_count_l2)
        self.assertIsNone(meter_statistics.voltage_swell_count_l3)
