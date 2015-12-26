from unittest import mock
import warnings

from django.core.management import call_command
from django.test import TestCase


class TestDsmrStatsPoller(TestCase):
    """ Deprecated legacy support for data poller compatiblity. """
    @mock.patch('serial.Serial.open')
    def test(self, serial_patch):
        # By using this side effect we can verify whether 'dsmr_stats_datalogger' is called.
        serial_patch.side_effect = RuntimeError("Test")

        with self.assertRaises(RuntimeError):
            call_command('dsmr_stats_poller')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            try:
                call_command('dsmr_stats_poller')
            except RuntimeError:
                pass

            self.assertEqual(len(w), 1)
            self.assertTrue(issubclass(w[-1].category, DeprecationWarning))
            self.assertEqual(
                w[-1].message,
                'dsmr_stats_poller is DEPRECATED, please use dsmr_stats_datalogger'
            )
