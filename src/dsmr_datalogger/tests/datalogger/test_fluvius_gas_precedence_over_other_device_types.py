from decimal import Decimal

from django.test import TestCase

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin
from dsmr_datalogger.tests.datalogger.test_fluvius_gas_channel_fallback import TestDatalogger as GasChannelFallback
from dsmr_parser.parsers import TelegramParser


class TestDatalogger(FakeDsmrReadingMixin, TestCase):
    """A non-gas MBus device (water, type 7) with a newer timestamp and different value must not be selected."""

    def setUp(self):
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(
            dsmr_version=DataloggerSettings.DSMR_BELGIUM_FLUVIUS,
            dsmr_extra_device_channel=None,
        )

    def _dsmr_dummy_data(self):
        # Channel 1: gas (type 3, 12:46:16). Channel 2: water (type 7), newer and reporting a very different value.
        lines = [
            line.replace("0-2:24.1.0(003)", "0-2:24.1.0(007)")
            for line in GasChannelFallback._dsmr_dummy_data(self)
            if not line.startswith("!")
        ]
        lines = [
            "0-2:24.2.3(230119124638W)(11734.607*m3)\r\n" if line.startswith("0-2:24.2.3") else line for line in lines
        ]
        crc = TelegramParser.crc16("".join(lines) + "!")
        return lines + ["!{:04X}".format(crc)]

    def test_gas_device_preferred_over_newer_non_gas_device(self):
        self._fake_dsmr_reading()
        reading = DsmrReading.objects.get()

        self.assertEqual(reading.extra_device_delivered, Decimal("734.607"))

    def test_pinned_channel_wins_over_gas_preference(self):
        DataloggerSettings.objects.all().update(
            dsmr_extra_device_channel=DataloggerSettings.DSMR_EXTRA_DEVICE_CHANNEL_2
        )

        self._fake_dsmr_reading()
        reading = DsmrReading.objects.get()

        self.assertEqual(reading.extra_device_delivered, Decimal("11734.607"))
