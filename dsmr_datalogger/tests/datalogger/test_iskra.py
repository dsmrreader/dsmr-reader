from unittest import mock
from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
import pytz

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics


class TestDatalogger(InterceptStdoutMixin, TestCase):
    """ Test Iskra meter, unknown DSMR version. """

    def _dsmr_dummy_data(self):
        return [
            "/ISk5\2MT382-1003\n",
            "\n",
            "0-0:96.1.1(xxxxxxxxxxx)\n",
            "1-0:1.8.1(01234.784*kWh)\n",
            "1-0:1.8.2(04321.725*kWh)\n",
            "1-0:2.8.1(00000.000*kWh)\n",
            "1-0:2.8.2(00000.002*kWh)\n",
            "0-0:96.14.0(0001)\n",
            "1-0:1.7.0(0000.36*kW)\n",
            "1-0:2.7.0(0000.00*kW)\n",
            "0-0:17.0.0(0999.00*kW)\n",
            "0-0:96.3.10(1)\n",
            "0-0:96.13.1()\n",
            "0-0:96.13.0()\n",
            "0-1:24.1.0(3)\n",
            "0-1:96.1.0(xxxxxxxxxxxx)\n",
            "0-1:24.3.0(160410130000)(00)(60)(1)(0-1:24.2.1)(m3)\n",
            "(07890.693)\n",
            "0-1:24.4.0(1)\n",
            "!\n",
        ]

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def _fake_dsmr_reading(self, serial_readline_mock, serial_open_mock):
        """ Fake & process an DSMR vX telegram reading. """
        serial_open_mock.return_value = None
        serial_readline_mock.side_effect = self._dsmr_dummy_data()

        self.assertFalse(DsmrReading.objects.exists())
        self._intercept_command_stdout('dsmr_datalogger')
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_creation(self):
        """ Test whether dsmr_datalogger can insert a reading. """
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    @mock.patch('django.utils.timezone.now')
    def test_reading_values(self, now_mock):
        """ Test whether dsmr_datalogger reads the correct values. """
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 4, 10, hour=14, minute=30, second=15)
        )

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp,
            datetime(2016, 4, 10, 12, 30, 15, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal('1234.784'))
        self.assertEqual(reading.electricity_returned_1, Decimal('0'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('4321.725'))
        self.assertEqual(reading.electricity_returned_2, Decimal('0.002'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.36'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2016, 4, 10, 11, 0, 0, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.extra_device_delivered, Decimal('7890.693'))

        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.electricity_tariff, 1)
        self.assertEqual(meter_statistics.power_failure_count, None)
        self.assertEqual(meter_statistics.long_power_failure_count, None)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, None)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, None)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, None)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, None)
