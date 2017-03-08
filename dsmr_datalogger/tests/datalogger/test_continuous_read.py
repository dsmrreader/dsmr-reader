from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading


class TestDatalogger(InterceptStdoutMixin, TestCase):
    """ Test whether the datalogger keeps handling telegrams. """

    def _dsmr_dummy_data(self):
        return [
            "/KFM5KAIFA-METER\r\n",
            "\r\n",
            "1-3:0.2.8(42)\r\n",
            "0-0:1.0.0(160303164347W)\r\n",
            "0-0:96.1.1(*******************************)\r\n",
            "1-0:1.8.1(001073.079*kWh)\r\n",
            "1-0:1.8.2(001263.199*kWh)\r\n",
            "1-0:2.8.1(000000.000*kWh)\r\n",
            "1-0:2.8.2(000000.000*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.143*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00006)\r\n",
            "0-0:96.7.9(00003)\r\n",
            "1-0:99.97.0(1)(0-0:96.7.19)(000101000001W)(2147483647*s)\r\n",
            "1-0:32.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:21.7.0(00.143*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "!A97E\n",

            "/KFM5KAIFA-METER\r\n",
            "\r\n",
            "1-3:0.2.8(42)\r\n",
            "0-0:1.0.0(160303164357W)\r\n",
            "0-0:96.1.1(*******************************)\r\n",
            "1-0:1.8.1(001073.079*kWh)\r\n",
            "1-0:1.8.2(001263.199*kWh)\r\n",
            "1-0:2.8.1(000000.000*kWh)\r\n",
            "1-0:2.8.2(000000.000*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.143*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00006)\r\n",
            "0-0:96.7.9(00003)\r\n",
            "1-0:99.97.0(1)(0-0:96.7.19)(000101000001W)(2147483657*s)\r\n",
            "1-0:32.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:21.7.0(00.143*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "!83CE\n",
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
        """ Test whether dsmr_datalogger can insert a reading for Kaifa DSMR v4.2. """
        self._fake_dsmr_reading()
        self.assertEqual(DsmrReading.objects.count(), 2)
