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
    """ Luxembourg Smarty meter. """
    def setUp(self):
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(dsmr_version=DataloggerSettings.DSMR_LUXEMBOURG_SMARTY)

    def _dsmr_dummy_data(self):
        return [
            "/Lux5\\ABCDEFG123_D\r\n",
            "\r\n",
            "1-3:0.2.8(42)\r\n",
            "0-0:1.0.0(191031142239W)\r\n",
            "0-0:42.0.0(12345678901234567890123456789012)\r\n",
            "1-0:1.8.0(005675.956*kWh)\r\n",
            "1-0:2.8.0(000000.002*kWh)\r\n",
            "1-0:3.8.0(000120.721*kvarh)\r\n",
            "1-0:4.8.0(000697.336*kvarh)\r\n",
            "1-0:1.7.0(03.074*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "1-0:3.7.0(00.000*kvar)\r\n",
            "1-0:4.7.0(00.000*kvar)\r\n",
            "0-0:17.0.0(27.600*kVA)\r\n",
            "0-0:96.3.10(1)\r\n",
            "0-0:96.13.0()\r\n",
            "0-0:96.13.2()\r\n",
            "0-0:96.13.3()\r\n",
            "0-0:96.13.4()\r\n",
            "0-0:96.13.5()\r\n",
            "!1BB8",
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
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 1, 1))
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(reading.timestamp, datetime(2019, 10, 31, 13, 22, 39, tzinfo=pytz.UTC))
        self.assertEqual(reading.electricity_delivered_1, Decimal('5675.956'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0.002'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('0'))
        self.assertEqual(reading.electricity_returned_2, Decimal('0'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('3.074'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertIsNone(reading.extra_device_timestamp)
        self.assertIsNone(reading.extra_device_delivered)
        self.assertIsNone(reading.phase_voltage_l1)
        self.assertIsNone(reading.phase_voltage_l2)
        self.assertIsNone(reading.phase_voltage_l3)
        self.assertIsNone(reading.phase_power_current_l1)
        self.assertIsNone(reading.phase_power_current_l2)
        self.assertIsNone(reading.phase_power_current_l3)

        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, '42')
        self.assertIsNone(meter_statistics.electricity_tariff)
        self.assertIsNone(meter_statistics.power_failure_count)
        self.assertIsNone(meter_statistics.long_power_failure_count)
        self.assertIsNone(meter_statistics.voltage_sag_count_l1)
        self.assertIsNone(meter_statistics.voltage_sag_count_l2)
        self.assertIsNone(meter_statistics.voltage_sag_count_l3)
        self.assertIsNone(meter_statistics.voltage_swell_count_l1)
        self.assertIsNone(meter_statistics.voltage_swell_count_l2)
        self.assertIsNone(meter_statistics.voltage_swell_count_l3)
