from unittest import mock

from django.test import TestCase
import serial

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.exceptions import InvalidTelegramError
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
import dsmr_datalogger.services.datalogger


class TestServices(TestCase):
    """
    Pycharm find-replace for samples:
    FIND:   \n
    REPL:   \\r\\n",\n"
    """
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
            "1-0:1.7.0(00.999*kW)\r\n",
            "1-0:2.7.0(01.332*kW)\r\n",
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
            "1-0:21.7.0(00.111*kW)\r\n",
            "1-0:41.7.0(00.333*kW)\r\n",
            "1-0:61.7.0(00.555*kW)\r\n",
            "1-0:22.7.0(00.222*kW)\r\n",
            "1-0:42.7.0(00.444*kW)\r\n",
            "1-0:62.7.0(00.666*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(xxxxxxxxxxxxx)\r\n",
            "0-1:24.2.1(151110190000W)(00845.206*m3)\r\n",
            "0-1:24.4.0(1)\r\n",
            "!45FF\n",
        ])

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
        dsmr_datalogger.services.datalogger.telegram_to_reading(data=telegram)

        # Should be populated now.
        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, '40')
        self.assertIsNotNone(meter_statistics.electricity_tariff)
        self.assertEqual(meter_statistics.electricity_tariff, 1)
        self.assertEqual(meter_statistics.power_failure_count, 3)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, 2)

    @mock.patch('dsmr_parser.parsers.TelegramParser.validate_checksum')
    def test_extra_devices_mbus_hack(self, _):
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
        dsmr_datalogger.services.datalogger.telegram_to_reading(data=''.join(fake_telegram))
        self.assertFalse(DsmrReading.objects.filter(extra_device_timestamp__isnull=True).exists())

        # Alter extra device m-bus to 2, 3 and 4.
        for current_mbus in (2, 3, 4):
            fake_telegram[-3] = "0-{}:24.2.1(151110190000W)(00845.206*m3)\r\n".format(current_mbus)
            self.assertNotIn("0-1:24.2.1(151110190000W)(00845.206*m3)\r\n", fake_telegram)

            dsmr_datalogger.services.datalogger.telegram_to_reading(data=''.join(fake_telegram))
            self.assertFalse(DsmrReading.objects.filter(extra_device_timestamp__isnull=True).exists())

    def test_validate_checksum(self):
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
            "!0000\n",  # Invalid
        ]

        with self.assertRaises(InvalidTelegramError):
            dsmr_datalogger.services.datalogger.telegram_to_reading(data=''.join(telegram))

        # Again, with the expected checksum.
        telegram[-1] = "!58C8\n"
        dsmr_datalogger.services.datalogger.telegram_to_reading(data=''.join(telegram))

    def test_telegram_logging_setting_coverage(self):
        """ Purely a coverage test. """
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(log_telegrams=True)
        dsmr_datalogger.services.datalogger.telegram_to_reading(data=self.fake_telegram)

    @mock.patch('dsmr_datalogger.signals.dsmr_reading_created.send_robust')
    def test_dsmr_reading_created_signal(self, send_robust_mock):
        self.assertFalse(send_robust_mock.called)
        dsmr_datalogger.services.datalogger.telegram_to_reading(data=self.fake_telegram)
        self.assertTrue(send_robust_mock.called)


class TestDsmrVersionMapping(InterceptStdoutMixin, TestCase):
    def test_dsmr_version_2_and_3(self):
        """ Test connection parameters for DSMR v2. """
        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.dsmr_version = DataloggerSettings.DSMR_VERSION_2_3
        datalogger_settings.save()

        self.assertEqual(DataloggerSettings.get_solo().dsmr_version, DataloggerSettings.DSMR_VERSION_2_3)

        connection_parameters = dsmr_datalogger.services.datalogger.get_dsmr_connection_parameters()
        self.assertEqual(connection_parameters['baudrate'], 9600)
        self.assertEqual(connection_parameters['bytesize'], serial.SEVENBITS)
        self.assertEqual(connection_parameters['parity'], serial.PARITY_EVEN)

    def test_dsmr_version_4_plus(self):
        """ Test connection parameters for DSMR v4+. """
        self.assertEqual(DataloggerSettings.get_solo().dsmr_version, DataloggerSettings.DSMR_VERSION_4_PLUS)

        connection_parameters = dsmr_datalogger.services.datalogger.get_dsmr_connection_parameters()
        self.assertEqual(connection_parameters['baudrate'], 115200)
        self.assertEqual(connection_parameters['bytesize'], serial.EIGHTBITS)
        self.assertEqual(connection_parameters['parity'], serial.PARITY_NONE)

    def test_dsmr_fluvius(self):
        DataloggerSettings.get_solo().update(dsmr_version=DataloggerSettings.DSMR_BELGIUM_FLUVIUS)
        self.assertEqual(DataloggerSettings.get_solo().dsmr_version, DataloggerSettings.DSMR_BELGIUM_FLUVIUS)

        connection_parameters = dsmr_datalogger.services.datalogger.get_dsmr_connection_parameters()
        self.assertEqual(connection_parameters['baudrate'], 115200)
        self.assertEqual(connection_parameters['bytesize'], serial.EIGHTBITS)
        self.assertEqual(connection_parameters['parity'], serial.PARITY_NONE)

    def test_dsmr_smarty(self):
        DataloggerSettings.get_solo().update(dsmr_version=DataloggerSettings.DSMR_LUXEMBOURG_SMARTY)
        self.assertEqual(DataloggerSettings.get_solo().dsmr_version, DataloggerSettings.DSMR_LUXEMBOURG_SMARTY)

        connection_parameters = dsmr_datalogger.services.datalogger.get_dsmr_connection_parameters()
        self.assertEqual(connection_parameters['baudrate'], 115200)
        self.assertEqual(connection_parameters['bytesize'], serial.EIGHTBITS)
        self.assertEqual(connection_parameters['parity'], serial.PARITY_NONE)
