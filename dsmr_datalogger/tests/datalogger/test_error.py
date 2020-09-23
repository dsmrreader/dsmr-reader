from decimal import Decimal
from unittest import mock

from django.utils import timezone
from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDataloggerError(FakeDsmrReadingMixin, InterceptStdoutMixin, TestCase):
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
            "0-0:96.1.1(12345678901234567890123456789012)\r\n",
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
            "!4BC6\n",
        ]

    def test_telegram_buffer_reset(self):
        """ Test whether an incomplete telegram gets dicarded. """
        self.assertFalse(DsmrReading.objects.exists())

        # Regression raises:   django.db.utils.IntegrityError: NOT NULL constraint failed:
        #                      dsmr_datalogger_dsmrreading.timestamp
        self._fake_dsmr_reading()
        self.assertEqual(DsmrReading.objects.count(), 1)


class TestDataloggerCrcError(FakeDsmrReadingMixin, InterceptStdoutMixin, TestCase):
    def _dsmr_dummy_data(self):
        """ Returns invalid telegram. """
        return [
            "/KFM5KAIFA-METER\r\n",
            "\r\n",
            "1-3:0.2.8(42)\r\n",
            "0-0:1.0.0(160303164347W)\r\n",
            "0-0:96.1.1(12345678901234567890123456789012)\r\n",
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

    def test_fail(self):
        """ Fake & process an DSMR vX telegram reading. """
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertFalse(DsmrReading.objects.exists())


class TestDataloggerDuplicateData(FakeDsmrReadingMixin, InterceptStdoutMixin, TestCase):
    """ Test Iskra meter, DSMR v5.0, with somewhat duplicate data. """

    def _dsmr_dummy_data(self):
        return [
            "/ISK5\\2M550T-1011\r\n",
            "\r\n",
            "1-3:0.2.8(50)\r\n",
            "0-0:1.0.0(170110204056W)\r\n",
            "0-0:96.1.1(xxx)\r\n",
            "1-0:1.8.1(000012.345*kWh)\r\n",
            "1-0:1.8.2(000067.890*kWh)\r\n",
            "1-0:2.8.1(000123.456*kWh)\r\n",
            "1-0:2.8.2(000789.012*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.321*k\n",
            "/ISK5\\2M550T-1011\r\n",
            "\r\n",
            "1-3:0.2.8(50)\r\n",
            "0-0:1.0.0(170110204057W)\r\n",
            "0-0:96.1.1(xxx)\r\n",
            "1-0:1.8.1(009012.345*kWh)\r\n",
            "1-0:1.8.2(009067.890*kWh)\r\n",
            "1-0:2.8.1(009123.456*kWh)\r\n",
            "1-0:2.8.2(009789.012*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.320*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00005)\r\n",
            "0-0:96.7.9(00002)\r\n",
            "1-0:99.97.0()\r\n",
            "1-0:32.32.0(00000)\r\n",
            "1-0:52.32.0(00000)\r\n",
            "1-0:72.32.0(00000)\r\n",
            "1-0:32.36.0(00001)\r\n",
            "1-0:52.36.0(00001)\r\n",
            "1-0:72.36.0(00001)\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:32.7.0(227.0*V)\r\n",
            "1-0:52.7.0(228.3*V)\r\n",
            "1-0:72.7.0(230.4*V)\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:51.7.0(000*A)\r\n",
            "1-0:71.7.0(000*A)\r\n",
            "1-0:21.7.0(00.152*kW)\r\n",
            "1-0:41.7.0(00.052*kW)\r\n",
            "1-0:61.7.0(00.118*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "1-0:42.7.0(00.000*kW)\r\n",
            "1-0:62.7.0(00.000*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(xxx)\r\n",
            "0-1:24.2.1(170110204009W)(00123.456*m3)\r\n",
            "!469F\r\n"
        ]

    def test_reading_creation(self):
        """ Test whether dsmr_datalogger can insert a reading. """
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    @mock.patch('django.utils.timezone.now')
    def test_reading_values(self, now_mock):
        """ Test whether dsmr_datalogger reads the correct values. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 2, 1, hour=0, minute=0, second=0))

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(
            reading.timestamp,
            timezone.datetime(2017, 1, 10, 19, 40, 57, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.electricity_delivered_1, Decimal('9012.345'))
        self.assertEqual(reading.electricity_returned_1, Decimal('9123.456'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('9067.890'))
        self.assertEqual(reading.electricity_returned_2, Decimal('9789.012'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('0.320'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(
            reading.extra_device_timestamp,
            timezone.datetime(2017, 1, 10, 19, 40, 9, tzinfo=pytz.UTC)
        )
        self.assertEqual(reading.extra_device_delivered, Decimal('123.456'))


class TestFutureTelegrams(FakeDsmrReadingMixin, InterceptStdoutMixin, TestCase):
    def _dsmr_dummy_data(self):
        return [
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(40)\r\n",
            "0-0:1.0.0(170102120000W)\r\n",  # <<< +1 day and some.
            "0-0:96.1.1(xxxxxxxxxxxxx)\r\n",
            "1-0:1.8.1(000510.747*kWh)\r\n",
            "1-0:2.8.1(000000.123*kWh)\r\n",
            "1-0:1.8.2(000500.013*kWh)\r\n",
            "1-0:2.8.2(000123.456*kWh)\r\n",
            "0-0:96.14.0(0001)\r\n",
            "1-0:1.7.0(00.192*kW)\r\n",
            "1-0:2.7.0(00.123*kW)\r\n",
            "0-0:17.0.0(999.9*kW)\r\n",
            "0-0:96.3.10(1)\r\n",
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
            "0-1:96.1.0(xxxxxxxxxxxxx)\r\n",
            "0-1:24.2.1(170102120000W)(00845.206*m3)\r\n",  # <<< +1 day and some.
            "0-1:24.4.0(1)\r\n",
            "!2998\n",
        ]

    @mock.patch('django.utils.timezone.now')
    def test_discard_telegram_with_future_timestamp(self, now_mock):
        """ Telegrams with timestamps in the (far) future should be rejected. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1, hour=9, minute=0, second=0))

        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()

        # It should be discarded.
        self.assertFalse(DsmrReading.objects.exists())
