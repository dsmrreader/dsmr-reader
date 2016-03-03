from unittest import mock
from datetime import datetime
from decimal import Decimal

from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics


class TestDatalogger(CallCommandStdoutMixin, TestCase):
    """ Test Landis+Gyr 350 DSMR v4.0. """
    def _dsmr_dummy_data(self):
        return [
            "/XMX5LGBBFFB123456789\n",
            "\n",
            "1-3:0.2.8(40)\n",
            "0-0:1.0.0(151110192959W)\n",
            "0-0:96.1.1(xxxxxxxxxxxxx)\n",
            "1-0:1.8.1(000510.747*kWh)\n",
            "1-0:2.8.1(000000.123*kWh)\n",
            "1-0:1.8.2(000500.013*kWh)\n",
            "1-0:2.8.2(000123.456*kWh)\n",
            "0-0:96.14.0(0001)\n",
            "1-0:1.7.0(00.192*kW)\n",
            "1-0:2.7.0(00.123*kW)\n",
            "0-0:17.0.0(999.9*kW)\n",
            "0-0:96.3.10(1)\n",
            "0-0:96.7.21(00003)\n",
            "0-0:96.7.9(00000)\n",
            "1-0:99.97.0(0)(0-0:96.7.19)\n",
            "1-0:32.32.0(00002)\n",
            "1-0:52.32.0(00002)\n",
            "1-0:72.32.0(00000)\n",
            "1-0:32.36.0(00000)\n",
            "1-0:52.36.0(00000)\n",
            "1-0:72.36.0(00000)\n",
            "0-0:96.13.1()\n",
            "0-0:96.13.0()\n",
            "1-0:31.7.0(000*A)\n",
            "1-0:51.7.0(000*A)\n",
            "1-0:71.7.0(001*A)\n",
            "1-0:21.7.0(00.000*kW)\n",
            "1-0:41.7.0(00.000*kW)\n",
            "1-0:61.7.0(00.192*kW)\n",
            "1-0:22.7.0(00.000*kW)\n",
            "1-0:42.7.0(00.000*kW)\n",
            "1-0:62.7.0(00.000*kW)\n",
            "0-1:24.1.0(003)\n",
            "0-1:96.1.0(xxxxxxxxxxxxx)\n",
            "0-1:24.2.1(151110190000W)(00845.206*m3)\n",
            "0-1:24.4.0(1)\n",
            "!D19A\n",
        ]

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def _fake_dsmr_reading(self, serial_readline_mock, serial_open_mock):
        """ Fake & process an DSMR vX telegram reading. """
        serial_open_mock.return_value = None
        serial_readline_mock.side_effect = self._dsmr_dummy_data()

        self._call_command_stdout('dsmr_datalogger')
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_creation(self):
        """ Test whether dsmr_datalogger can insert a reading for Landis+Gyr 350 DSMR v4.0. """
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
            datetime(2015, 11, 10, 18, 29, 59, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal('510.747'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0.123'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('500.013'))
        self.assertEqual(reading.electricity_returned_2, Decimal('123.456'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.192'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0.123'))
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2015, 11, 10, 18, 0, 0, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.extra_device_delivered, Decimal('845.206'))

        # Different data source.
        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.electricity_tariff, Decimal('1'))
        self.assertEqual(meter_statistics.power_failure_count, 3)
        self.assertEqual(meter_statistics.long_power_failure_count, 0)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, 0)
