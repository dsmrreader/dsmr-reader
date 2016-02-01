from unittest import mock
import warnings

from django.core.management import call_command
from django.test import TestCase


class TestDeprecation(TestCase):
    DEPRECATED_COMMANDS = ['dsmr_stats_datalogger', 'dsmr_stats_compactor']

    @mock.patch('serial.Serial.open')
    def test_datalogger(self, serial_patch):
        """ Test dsmr_stats_datalogger deprecation and fallback. """
        # By using this side effect we can verify whether 'dsmr_stats_datalogger' is called.
        serial_patch.side_effect = RuntimeError("Test")

        for current_command in self.DEPRECATED_COMMANDS:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")

                try:
                    call_command(current_command)
                except RuntimeError:
                    pass

                self.assertEqual(len(w), 1)
                self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
