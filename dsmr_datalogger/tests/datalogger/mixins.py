from datetime import datetime
from unittest import mock
from unittest.case import TestCase

import pytz
from django.utils import timezone
from serial import Serial

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import DataloggerSettings


class FakeDsmrReadingMixin(InterceptCommandStdoutMixin, TestCase):
    """ Mixin to ease faking reading serial input. """

    def _dsmr_dummy_data(self):
        raise NotImplementedError('Override this in parent class')

    @mock.patch('serial.serial_for_url')
    def _fake_dsmr_reading(self, serial_for_url_mock, run_once=True):
        """ Fake & process an DSMR vX telegram reading. """
        cli_serial = Serial()
        cli_serial.read = mock.MagicMock(
            # Convert to bytes.
            side_effect=[bytes(x, 'latin_1') for x in self._dsmr_dummy_data()]
        )
        serial_for_url_mock.return_value = cli_serial

        self._intercept_command_stdout('dsmr_datalogger', run_once=run_once)

    def _reading_with_override_telegram_timestamp_active(self, now_mock) -> DsmrReading:
        """ For DRY. Returns the reading. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2021, 1, 15, 12, 34, 56, 0))

        datalogger_settings = DataloggerSettings.get_solo()
        datalogger_settings.update(override_telegram_timestamp=True)

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

        reading = DsmrReading.objects.get()
        self.assertEqual(reading.timestamp, datetime(2021, 1, 15, 11, 34, 56, 0, tzinfo=pytz.UTC))  # CET > UTC

        return reading
