from unittest import mock
import warnings

from django.core.management import call_command
from django.test import TestCase


class TestDeprecation(TestCase):
    @mock.patch('serial.Serial.open')
    def test(self, serial_patch):
        """ Test dsmr_stats_datalogger deprecation and fallback. """
        # By using this side effect we can verify whether 'dsmr_stats_datalogger' is called.
        serial_patch.side_effect = RuntimeError("Test")

        with self.assertRaises(RuntimeError):
            call_command('dsmr_stats_datalogger')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                call_command('dsmr_stats_datalogger')
            except RuntimeError:
                pass

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
