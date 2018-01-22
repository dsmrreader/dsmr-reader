from decimal import Decimal
from unittest import mock

from django.core.management import CommandError
from django.test import TestCase
from django.utils import timezone
import serial
import pytz

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.exceptions import InvalidTelegramError
import dsmr_datalogger.services


class TestDsmrDataloggerTracking(InterceptStdoutMixin, TestCase):
    def test_tracking_disabled(self):
        """ Test whether datalogger can bij stopped by changing track setting. """
        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.track = False
        datalogger_settings.save()

        # Datalogger should crash with error.
        with self.assertRaisesMessage(CommandError, 'Datalogger tracking is DISABLED!'):
            self._intercept_command_stdout('dsmr_datalogger', run_once=True)


class TestServices(TestCase):
    fake_telegram = None

    def setUp(self):
        self.fake_telegram = ''.join([
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(40)\r\n",
            "0-0:1.0.0(151110192959W)\r\n",
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
            "0-1:24.2.1(151110190000W)(00845.206*m3)\r\n",
            "0-1:24.4.0(1)\r\n",
            "!8CC9\n",
        ])

    def test_reading_timestamp_to_datetime(self):
        result = dsmr_datalogger.services.reading_timestamp_to_datetime('151110192959W')
        expected_result = timezone.make_aware(timezone.datetime(2015, 11, 10, 19, 29, 59))
        self.assertEqual(result, expected_result)
        self.assertEqual(result.tzinfo, pytz.utc)

        result = dsmr_datalogger.services.reading_timestamp_to_datetime('160401203040W')
        expected_result = timezone.make_aware(timezone.datetime(2016, 4, 1, 20, 30, 40))
        self.assertEqual(result, expected_result)
        self.assertEqual(result.tzinfo, pytz.utc)

        # Summer time.
        result = dsmr_datalogger.services.reading_timestamp_to_datetime('160327042016S')
        expected_result = timezone.make_aware(timezone.datetime(2016, 3, 27, 4, 20, 16))
        self.assertEqual(result, expected_result)
        self.assertEqual(result.tzinfo, pytz.utc)

        """ Summer to winter transition is hard in DST, because the input is not UTC. """
        # Last hour before winter time.
        result = dsmr_datalogger.services.reading_timestamp_to_datetime('161030020000S')
        expected_result = timezone.datetime(2016, 10, 30, 0, tzinfo=pytz.utc)
        self.assertEqual(result, expected_result)

        # Last second before winter time.
        result = dsmr_datalogger.services.reading_timestamp_to_datetime('161030025959S')
        expected_result = timezone.datetime(2016, 10, 30, 0, 59, 59, tzinfo=pytz.utc)
        self.assertEqual(result, expected_result)

        # First second in winter time.
        result = dsmr_datalogger.services.reading_timestamp_to_datetime('161030020000W')
        expected_result = timezone.datetime(2016, 10, 30, 1, tzinfo=pytz.utc)
        self.assertEqual(result, expected_result)

        # Last second of DST transition.
        result = dsmr_datalogger.services.reading_timestamp_to_datetime('161030025959W')
        expected_result = timezone.datetime(2016, 10, 30, 1, 59, 59, tzinfo=pytz.utc)
        self.assertEqual(result, expected_result)

    def test_track_meter_statistics(self):
        telegram = ''.join([
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(40)\r\n",
            "0-0:1.0.0(151110192959W)\r\n",
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
            "1-0:21.7.0(00.000*kW)\r\n",
            "1-0:41.7.0(00.000*kW)\r\n",
            "1-0:61.7.0(00.192*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "1-0:42.7.0(00.000*kW)\r\n",
            "1-0:62.7.0(00.000*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(xxxxxxxxxxxxx)\r\n",
            "0-1:24.2.1(151110190000W)(00845.206*m3)\r\n",
            "0-1:24.4.0(1)\r\n",
            "!AF0C\n",
        ])

        self.assertIsNone(MeterStatistics.get_solo().electricity_tariff)  # Empty model in DB.
        dsmr_datalogger.services.telegram_to_reading(data=telegram)

        # Should be populated now.
        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, '40')
        self.assertIsNotNone(meter_statistics.electricity_tariff)
        self.assertEqual(meter_statistics.electricity_tariff, 1)
        self.assertEqual(meter_statistics.power_failure_count, 3)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, 2)

    def test_track_phases(self):
        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.track_phases = False
        datalogger_settings.save()

        self.assertFalse(DsmrReading.objects.all().exists())

        dsmr_datalogger.services.telegram_to_reading(data=self.fake_telegram)

        my_reading = DsmrReading.objects.get()
        self.assertIsNone(my_reading.phase_currently_delivered_l1)
        self.assertIsNone(my_reading.phase_currently_delivered_l2)
        self.assertIsNone(my_reading.phase_currently_delivered_l3)

        # Try again, but now with tracking settings enabled.
        DataloggerSettings.objects.all().update(track_phases=True)

        DsmrReading.objects.all().delete()
        dsmr_datalogger.services.telegram_to_reading(data=self.fake_telegram)

        # Should be populated now.
        my_reading = DsmrReading.objects.get()
        self.assertEqual(my_reading.phase_currently_delivered_l1, Decimal('0.123'))
        self.assertEqual(my_reading.phase_currently_delivered_l2, Decimal('0.456'))
        self.assertEqual(my_reading.phase_currently_delivered_l3, Decimal('0.789'))

    @mock.patch('dsmr_datalogger.services.verify_telegram_checksum')
    def test_extra_devices_mbus_hack(self, *mocks):
        """ Verify that the hack issue #92 is working. """
        fake_telegram = [
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(40)\r\n",
            "0-0:1.0.0(151110192959W)\r\n",
            "0-0:96.1.1(123456789012345678901234567890)\r\n",
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
            "0-1:96.1.0(098765432109876543210987654321)\r\n",
            "0-1:24.2.1(151110190000W)(00845.206*m3)\r\n",
            "0-1:24.4.0(1)\r\n",
            "!6013\n",
        ]
        self.assertFalse(DsmrReading.objects.exists())
        dsmr_datalogger.services.telegram_to_reading(data=''.join(fake_telegram))
        self.assertFalse(DsmrReading.objects.filter(extra_device_timestamp__isnull=True).exists())

        # Alter extra device m-bus to 2, 3 and 4.
        for current_mbus in (2, 3, 4):
            fake_telegram[-3] = "0-{}:24.2.1(151110190000W)(00845.206*m3)\r\n".format(current_mbus)
            self.assertNotIn("0-1:24.2.1(151110190000W)(00845.206*m3)\r\n", fake_telegram)

            dsmr_datalogger.services.telegram_to_reading(data=''.join(fake_telegram))
            self.assertFalse(DsmrReading.objects.filter(extra_device_timestamp__isnull=True).exists())

    def test_verify_telegram_checksum(self):
        """ Verify that CRC checks. """
        telegram = [
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(40)\r\n",
            "0-0:1.0.0(151110192959W)\r\n",
            "0-0:96.1.1(123456789012345678901234567890)\r\n",
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
            "1-0:21.7.0(00.000*kW)\r\n",
            "1-0:41.7.0(00.000*kW)\r\n",
            "1-0:61.7.0(00.192*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "1-0:42.7.0(00.000*kW)\r\n",
            "1-0:62.7.0(00.000*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(098765432109876543210987654321)\r\n",
            "0-1:24.2.1(151110190000W)(00845.206*m3)\r\n",
            "0-1:24.4.0(1)\r\n",
            "!D19A\n",
        ]

        with self.assertRaises(InvalidTelegramError):
            # Empty.
            dsmr_datalogger.services.verify_telegram_checksum(data='')

        with self.assertRaises(InvalidTelegramError):
            # Invalid checksum.
            dsmr_datalogger.services.verify_telegram_checksum(data=''.join(telegram))

        # Again, with the correct checksum.
        telegram[-1] = "!58C8\n"
        dsmr_datalogger.services.verify_telegram_checksum(data=''.join(telegram))

    @mock.patch('django.conf.settings.DSMRREADER_LOG_TELEGRAMS')
    def test_telegram_logging_setting_coverage(self, settings_mock):
        """ Purely a coverage test. """
        settings_mock.return_value = True
        dsmr_datalogger.services.telegram_to_reading(data=self.fake_telegram)


class TestDsmrVersionMapping(InterceptStdoutMixin, TestCase):
    def test_dsmr_version_2(self):
        """ Test connection parameters for DSMR v2. """
        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.dsmr_version = DataloggerSettings.DSMR_VERSION_2
        datalogger_settings.save()

        self.assertEqual(DataloggerSettings.get_solo().dsmr_version, DataloggerSettings.DSMR_VERSION_2)

        connection_parameters = dsmr_datalogger.services.get_dsmr_connection_parameters()
        self.assertEqual(connection_parameters['baudrate'], 9600)
        self.assertEqual(connection_parameters['bytesize'], serial.SEVENBITS)
        self.assertEqual(connection_parameters['parity'], serial.PARITY_EVEN)

    def test_dsmr_version_4_plus(self):
        """ Test connection parameters for DSMR v4+. """
        self.assertEqual(DataloggerSettings.get_solo().dsmr_version, DataloggerSettings.DSMR_VERSION_4_PLUS)

        connection_parameters = dsmr_datalogger.services.get_dsmr_connection_parameters()
        self.assertEqual(connection_parameters['baudrate'], 115200)
        self.assertEqual(connection_parameters['bytesize'], serial.EIGHTBITS)
        self.assertEqual(connection_parameters['parity'], serial.PARITY_NONE)
