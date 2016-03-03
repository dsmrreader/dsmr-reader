from unittest import mock
from datetime import datetime
from decimal import Decimal

from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics


class TestKaifaDsmrV42Datalogger(CallCommandStdoutMixin, TestCase):
    """ Test Kaifa DSMR v4.2, without gas support. """

    def _dsmr_dummy_data(self):
        return [
            "/KFM5KAIFA-METER\n",
            "\n",
            "1-3:0.2.8(42)\n",
            "0-0:1.0.0(160303164347W)\n",
            "0-0:96.1.1(*******************************)\n",
            "1-0:1.8.1(001073.079*kWh)\n",
            "1-0:1.8.2(001263.199*kWh)\n",
            "1-0:2.8.1(000000.000*kWh)\n",
            "1-0:2.8.2(000000.000*kWh)\n",
            "0-0:96.14.0(0002)\n",
            "1-0:1.7.0(00.143*kW)\n",
            "1-0:2.7.0(00.000*kW)\n",
            "0-0:96.7.21(00006)\n",
            "0-0:96.7.9(00003)\n",
            "1-0:99.97.0(1)(0-0:96.7.19)(000101000001W)(2147483647*s)\n",
            "1-0:32.32.0(00000)\n",
            "1-0:32.36.0(00000)\n",
            "0-0:96.13.1()\n",
            "0-0:96.13.0()\n",
            "1-0:31.7.0(000*A)\n",
            "1-0:21.7.0(00.143*kW)\n",
            "1-0:22.7.0(00.000*kW)\n",
            "!74B0\n",
        ]

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def _fake_dsmr_reading(self, serial_readline_mock, serial_open_mock):
        """ Fake & process an DSMR vX telegram reading. """
        serial_open_mock.return_value = None
        serial_readline_mock.side_effect = self._dsmr_dummy_data()

        self.assertFalse(DsmrReading.objects.exists())
        self._call_command_stdout('dsmr_datalogger')
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_creation(self):
        """ Test whether dsmr_datalogger can insert a reading for Kaifa DSMR v4.2. """
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_values(self):
        """ Test whether dsmr_datalogger reads the correct values. """
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp,
            datetime(2016, 3, 3, 15, 43, 47, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal('1073.079'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('1263.199'))
        self.assertEqual(reading.electricity_returned_2, Decimal('0'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.143'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(reading.extra_device_timestamp, None)
        self.assertEqual(reading.extra_device_delivered, None)

        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.electricity_tariff, 2)
        self.assertEqual(meter_statistics.power_failure_count, 6)
        self.assertEqual(meter_statistics.long_power_failure_count, 3)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, None)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, None)
