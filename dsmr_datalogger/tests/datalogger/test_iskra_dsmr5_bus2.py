from unittest import mock
from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
import pytz

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings


class TestDatalogger(InterceptStdoutMixin, TestCase):
    """ Iskra meter, DSMRv5, gas on bus 2. """
    def setUp(self):
        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.dsmr_version = DataloggerSettings.DSMR_VERSION_4_PLUS
        datalogger_settings.save()

    def _dsmr_dummy_data(self):
        return [
            "/ISK5\2M550E-1012\r\n",
            "\r\n",
            "1-3:0.2.8(50)\r\n",
            "0-0:1.0.0(191108145519W)\r\n",
            "0-0:96.1.1(12345678901234567890123456789012)\r\n",
            "1-0:1.8.1(001043.936*kWh)\r\n",
            "1-0:1.8.2(000870.706*kWh)\r\n",
            "1-0:2.8.1(000000.000*kWh)\r\n",
            "1-0:2.8.2(000000.000*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.189*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00008)\r\n",
            "0-0:96.7.9(00003)\r\n",
            "1-0:99.97.0(1)(0-0:96.7.19)(190115011853W)(0000000389*s)\r\n",
            "1-0:32.32.0(00005)\r\n",
            "1-0:32.36.0(00001)\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:32.7.0(235.4*V)\r\n",
            "1-0:31.7.0(001*A)\r\n",
            "1-0:21.7.0(00.190*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0()\r\n",
            "0-1:24.2.1(700101010000W)(00000000)\r\n",
            "0-2:24.1.0(003)\r\n",
            "0-2:96.1.0(12345678901234567890123456789012)\r\n",
            "0-2:24.2.1(191108145505W)(00241.773*m3)\r\n",
            "!09AA\n",
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
        """ Test whether dsmr_datalogger can insert a reading. """
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    @mock.patch('django.utils.timezone.now')
    def test_reading_values(self, now_mock):
        """ Test whether dsmr_datalogger reads the correct values. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2019, 11, 8, hour=20))

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()

        self.assertEqual(reading.timestamp, datetime(2019, 11, 8, 13, 55, 19, tzinfo=pytz.UTC))
        self.assertEqual(reading.electricity_delivered_1, Decimal('1043.936'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('870.706'))
        self.assertEqual(reading.electricity_returned_2, Decimal('0'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.189'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(reading.extra_device_timestamp, datetime(2019, 11, 8, 13, 55, 5, tzinfo=pytz.UTC))
        self.assertEqual(reading.extra_device_delivered, Decimal('241.773'))
        self.assertEqual(reading.phase_voltage_l1, Decimal('235.4'))
        self.assertIsNone(reading.phase_voltage_l2)
        self.assertIsNone(reading.phase_voltage_l3)

        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, '50')
        self.assertEqual(meter_statistics.electricity_tariff, 2)
        self.assertEqual(meter_statistics.power_failure_count, 8)
        self.assertEqual(meter_statistics.long_power_failure_count, 3)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 5)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, None)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 1)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, None)
