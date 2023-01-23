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
    """Belgium Fluvius meter (polyphase) with two gas devices (one inactive)."""

    def setUp(self):
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(
            dsmr_version=DataloggerSettings.DSMR_BELGIUM_FLUVIUS,
            dsmr_extra_device_channel=DataloggerSettings.DSMR_EXTRA_DEVICE_CHANNEL_1,
        )

    def _dsmr_dummy_data(self):
        return [
            "/FLU5\253769484_A\r\n",
            "\r\n",
            "0-0:96.1.4(012345678901234567890123456789)\r\n",
            "0-0:96.1.1(012345678901234567890123456789)\r\n",
            "0-0:1.0.0(230119124638W)\r\n",
            "1-0:1.8.1(004423.770*kWh)\r\n",
            "1-0:1.8.2(002607.237*kWh)\r\n",
            "1-0:2.8.1(001194.693*kWh)\r\n",
            "1-0:2.8.2(000755.554*kWh)\r\n",
            "0-0:96.14.0(0001)\r\n",
            "1-0:1.4.0(00.000*kW)\r\n",
            "1-0:1.6.0(230116090000W)(11.173*kW)\r\n",
            "0-0:98.1.0(1)(1-0:1.6.0)(1-0:1.6.0)(230101000000W)(221230114500W)(13.603*kW)\r\n",
            "1-0:1.7.0(00.000*kW)\r\n",
            "1-0:2.7.0(00.204*kW)\r\n",
            "1-0:21.7.0(00.000*kW)\r\n",
            "1-0:41.7.0(00.177*kW)\r\n",
            "1-0:61.7.0(00.109*kW)\r\n",
            "1-0:22.7.0(00.491*kW)\r\n",
            "1-0:42.7.0(00.000*kW)\r\n",
            "1-0:62.7.0(00.000*kW)\r\n",
            "1-0:32.7.0(234.3*V)\r\n",
            "1-0:52.7.0(234.2*V)\r\n",
            "1-0:72.7.0(234.3*V)\r\n",
            "1-0:31.7.0(002.18*A)\r\n",
            "1-0:51.7.0(000.93*A)\r\n",
            "1-0:71.7.0(000.60*A)\r\n",
            "0-0:96.3.10(1)\r\n",
            "0-0:17.0.0(999.9*kW)\r\n",
            "1-0:31.4.0(999*A)\r\n",
            "0-0:96.13.0()\r\n",
            # Active gas device
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.1(012345678901234567890123456789)\r\n",
            "0-1:24.4.0(1)\r\n",
            "0-1:24.2.3(230119124616W)(00734.607*m3)\r\n",
            # Inactive/stale gas device
            "0-2:24.1.0(003)\r\n",
            "0-2:96.1.1(012345678901234567890123456789)\r\n",
            "0-2:24.4.0(1)\r\n",
            "0-2:24.2.3(230119124005W)(00000.000*m3)\r\n",
            "!B315",
        ]

    def test_reading_creation(self):
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    @mock.patch("django.utils.timezone.now")
    def test_reading_values(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2023, 1, 20))
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp, datetime(2023, 1, 19, 11, 46, 38, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal("4423.770"))
        self.assertEqual(reading.electricity_returned_1, Decimal("1194.693"))
        self.assertEqual(reading.electricity_delivered_2, Decimal("2607.237"))
        self.assertEqual(reading.electricity_returned_2, Decimal("755.554"))
        self.assertEqual(reading.electricity_currently_delivered, Decimal("0"))
        self.assertEqual(reading.electricity_currently_returned, Decimal("0.204"))
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2023, 1, 19, 11, 46, 16, tzinfo=pytz.UTC),
        )
        self.assertEqual(reading.extra_device_delivered, Decimal("734.607"))
        self.assertEqual(reading.phase_voltage_l1, Decimal("234.3"))
        self.assertEqual(reading.phase_voltage_l2, Decimal("234.2"))
        self.assertEqual(reading.phase_voltage_l3, Decimal("234.3"))
        self.assertEqual(reading.phase_power_current_l1, 2)
        self.assertEqual(reading.phase_power_current_l2, 0)
        self.assertEqual(reading.phase_power_current_l3, 0)

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
