from unittest import mock

from django.test import TestCase, override_settings

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDataloggerCoverage(
    FakeDsmrReadingMixin, InterceptCommandStdoutMixin, TestCase
):
    def _dsmr_dummy_data(self):
        return "".join(
            [
                "/-!",
            ]
        )

    def setUp(self):
        # Skip update mixin due to restart signal.
        DataloggerSettings.objects.all().update(
            process_sleep=0.1,
            restart_required=False,
        )

    @override_settings(DSMRREADER_DATALOGGER_MIN_SLEEP_FOR_RECONNECT=0)
    @mock.patch("dsmr_datalogger.services.datalogger.telegram_to_reading")
    def test_dsmr_datalogger_reconnect(self, service_mock):
        service_mock.side_effect = [None, None, StopIteration()]

        self._fake_dsmr_reading()

    @override_settings(DSMRREADER_DATALOGGER_MIN_SLEEP_FOR_RECONNECT=999)
    @mock.patch("dsmr_datalogger.services.datalogger.telegram_to_reading")
    def test_dsmr_datalogger_persistent(self, service_mock):
        service_mock.side_effect = [None, None, StopIteration()]

        self._fake_dsmr_reading()
