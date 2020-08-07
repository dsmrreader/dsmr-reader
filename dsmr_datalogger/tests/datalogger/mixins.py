from unittest import mock
from unittest.case import TestCase

from serial import Serial

from dsmr_backend.tests.mixins import InterceptStdoutMixin


class FakeDsmrReadingMixin(InterceptStdoutMixin, TestCase):
    """ Mixin to ease faking reading serial input. """
    def _dsmr_dummy_data(self):
        raise NotImplementedError('Override this in parent class')

    @mock.patch('serial.serial_for_url')
    def _fake_dsmr_reading(self, serial_for_url_mock):
        """ Fake & process an DSMR vX telegram reading. """
        cli_serial = Serial()
        cli_serial.read = mock.MagicMock(
            # Convert to bytes.
            side_effect=[bytes(x, 'latin_1') for x in self._dsmr_dummy_data()]
        )
        serial_for_url_mock.return_value = cli_serial

        self._intercept_command_stdout('dsmr_datalogger', run_once=True)
