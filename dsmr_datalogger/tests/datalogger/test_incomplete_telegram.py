from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading


class TestDataloggerIncompleteTelegram(InterceptStdoutMixin, TestCase):
    """ Test INCOMPLETE telegram. """

    def _dsmr_dummy_data(self):
        return [
            # We start halfway, forcing us to discard/ignore it.
            "1-0:99.97.0(1)(0-0:96.7.19)(000101000001W)(2147483647*s)\n",
            "1-0:32.32.0(00000)\n",
            "1-0:32.36.0(00000)\n",
            "0-0:96.13.1()\n",
            "0-0:96.13.0()\n",
            "1-0:31.7.0(000*A)\n",
            "1-0:21.7.0(00.143*kW)\n",
            "1-0:22.7.0(00.000*kW)\n",
            "!74B0\n",

            # 10 seconds later we should see this one.
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
        self._intercept_command_stdout('dsmr_datalogger')

    def test_telegram_buffer_reset(self):
        """ Test whether an incomplete telegram gets dicarded. """
        self.assertFalse(DsmrReading.objects.exists())

        # Regression raises:   django.db.utils.IntegrityError: NOT NULL constraint failed:
        #                      dsmr_datalogger_dsmrreading.timestamp
        self._fake_dsmr_reading()
        self.assertEqual(DsmrReading.objects.count(), 1)
