from unittest import mock

from serial.serialutil import SerialException
from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading


class TestDataloggerError(InterceptStdoutMixin, TestCase):
    def _dsmr_dummy_data(self):
        """ Returns INCOMPLETE telegram. """
        return [
            # We start halfway, forcing us to discard/ignore it.
            "1-0:99.97.0(1)(0-0:96.7.19)(000101000001W)(2147483647*s)\r\n",
            "1-0:32.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:21.7.0(00.143*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "!74B0\n",

            # 10 seconds later we should see this one.
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
        ]

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def _fake_dsmr_reading(self, serial_readline_mock, serial_open_mock):
        """ Fake & process an DSMR vX telegram reading. """
        serial_open_mock.return_value = None
        serial_readline_mock.side_effect = self._dsmr_dummy_data()
        self._intercept_command_stdout('dsmr_datalogger')

    def test_telegram_buffer_reset(self):
        """ Test whether an incomplete telegram gets dicarded. """
        self.assertFalse(DsmrReading.objects.exists())

        # Regression raises:   django.db.utils.IntegrityError: NOT NULL constraint failed:
        #                      dsmr_datalogger_dsmrreading.timestamp
        self._fake_dsmr_reading()
        self.assertEqual(DsmrReading.objects.count(), 1)

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def test_interrupt(self, serial_readline_mock, serial_open_mock):
        """ Test whether interrupts are handled. """
        serial_open_mock.return_value = None

        # First call raises expected exception, second call should just return data.
        eintr_error = SerialException('read failed: [Errno 4] Interrupted system call')
        serial_readline_mock.side_effect = [eintr_error] + self._dsmr_dummy_data()
        self.assertFalse(DsmrReading.objects.exists())

        self._intercept_command_stdout('dsmr_datalogger')
        self.assertTrue(DsmrReading.objects.exists())

        # Everything else should be reraised.
        serial_readline_mock.side_effect = SerialException('Unexpected error from Serial')

        DsmrReading.objects.all().delete()
        self.assertFalse(DsmrReading.objects.exists())

        with self.assertRaises(SerialException):
            self._intercept_command_stdout('dsmr_datalogger')

        self.assertFalse(DsmrReading.objects.exists())


class TestDataloggerCrcError(InterceptStdoutMixin, TestCase):
    def _dsmr_dummy_data(self):
        """ Returns invalid telegram. """
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
            "!ABCD\n",  # <<< Invalid CRC.
        ]

    @mock.patch('serial.Serial.open')
    @mock.patch('serial.Serial.readline')
    def test_fail(self, serial_readline_mock, serial_open_mock):
        """ Fake & process an DSMR vX telegram reading. """
        serial_open_mock.return_value = None
        serial_readline_mock.side_effect = self._dsmr_dummy_data()

        self.assertFalse(DsmrReading.objects.exists())

        self._intercept_command_stdout('dsmr_datalogger')

        self.assertFalse(DsmrReading.objects.exists())
