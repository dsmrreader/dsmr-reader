from django.core.management import CommandError
from django.test import TestCase
import serial

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_datalogger.services


class TestDsmrDataloggerTracking(CallCommandStdoutMixin, TestCase):
    def test_tracking_disabled(self):
        """ Test whether datalogger can bij stopped by changing track setting. """
        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.track = False
        datalogger_settings.save()

        # Datalogger should crash with error.
        with self.assertRaisesMessage(CommandError, 'Datalogger tracking is DISABLED!'):
            self._call_command_stdout('dsmr_datalogger')


class TestDsmrVersionMapping(CallCommandStdoutMixin, TestCase):
    def test_dsmr_version_3(self):
        """ Test connection parameters for DSMR v2/3. """
        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.dsmr_version = DataloggerSettings.DSMR_VERSION_3
        datalogger_settings.save()

        self.assertEqual(
            DataloggerSettings.get_solo().dsmr_version, DataloggerSettings.DSMR_VERSION_3
        )

        connection_parameters = dsmr_datalogger.services.get_dsmr_connection_parameters()
        self.assertEqual(connection_parameters['baudrate'], 9600)
        self.assertEqual(connection_parameters['bytesize'], serial.SEVENBITS)
        self.assertEqual(connection_parameters['parity'], serial.PARITY_EVEN)

    def test_dsmr_version_4(self):
        """ Test connection parameters for DSMR v4. """
        self.assertEqual(
            DataloggerSettings.get_solo().dsmr_version, DataloggerSettings.DSMR_VERSION_4
        )

        connection_parameters = dsmr_datalogger.services.get_dsmr_connection_parameters()
        self.assertEqual(connection_parameters['baudrate'], 115200)
        self.assertEqual(connection_parameters['bytesize'], serial.EIGHTBITS)
        self.assertEqual(connection_parameters['parity'], serial.PARITY_NONE)
