from unittest import mock
from datetime import datetime
from decimal import Decimal

from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings


class TestDatalogger(InterceptStdoutMixin, TestCase):
    """ Test Landis+Gyr 350 DSMR v4.2. """

    def _dsmr_dummy_data(self):
        return [
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(42)\r\n",
            "0-0:1.0.0(160210203034W)\r\n",
            "0-0:96.1.1(123456789012345678901234567890)\r\n",
            "1-0:1.8.1(000756.849*kWh)\r\n",
            "1-0:2.8.1(000000.000*kWh)\r\n",
            "1-0:1.8.2(000714.405*kWh)\r\n",
            "1-0:2.8.2(000000.000*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.111*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
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
            "1-0:22.7.0(00.000*kW)\r\n",
            "1-0:42.7.0(00.000*kW)\r\n",
            "1-0:62.7.0(00.000*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(098765432109876543210987654321)\r\n",
            "0-1:24.2.1(160210200000W)(01197.484*m3)\r\n",
            "!48F4\n",
        ]

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def _fake_dsmr_reading(self, serial_readline_mock, serial_open_mock):
        """ Fake & process an DSMR vX telegram reading. """
        serial_open_mock.return_value = None
        serial_readline_mock.side_effect = self._dsmr_dummy_data()

        self.assertFalse(DsmrReading.objects.exists())
        self._intercept_command_stdout('dsmr_datalogger', run_once=True)
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_creation(self):
        """ Test whether dsmr_datalogger can insert a reading for Landis+Gyr 350 DSMR v4.2. """
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_values(self):
        """ Test whether dsmr_datalogger reads the correct values. """
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(track_phases=True)

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp,
            datetime(2016, 2, 10, 19, 30, 34, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal('756.849'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('714.405'))
        self.assertEqual(reading.electricity_returned_2, Decimal('0'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.111'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2016, 2, 10, 19, 0, 0, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.extra_device_delivered, Decimal('1197.484'))
        self.assertEqual(reading.phase_currently_delivered_l1, Decimal('0.123'))
        self.assertEqual(reading.phase_currently_delivered_l2, Decimal('0.456'))
        self.assertEqual(reading.phase_currently_delivered_l3, Decimal('0.789'))

        # Different data source.
        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, '42')
        self.assertEqual(meter_statistics.electricity_tariff, 2)
        self.assertEqual(meter_statistics.power_failure_count, 3)
        self.assertEqual(meter_statistics.long_power_failure_count, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, 0)

    @mock.patch('dsmr_datalogger.signals.raw_telegram.send_robust')
    def test_raw_telegram_signal_sent(self, signal_mock):
        self.assertFalse(signal_mock.called)
        self._fake_dsmr_reading()
        self.assertTrue(signal_mock.called)
