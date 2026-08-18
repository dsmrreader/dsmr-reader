from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from zoneinfo import ZoneInfo

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDatalogger(FakeDsmrReadingMixin, TestCase):
    """Belgium Fluvius meter configured for a gas channel that isn't present in the telegram.

    _select_extra_device_reading() must fall back to an available MBus channel instead of
    silently dropping the extra device reading.
    """

    def setUp(self):
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(
            dsmr_version=DataloggerSettings.DSMR_BELGIUM_FLUVIUS,
            # Only channels 1 and 2 are present below, channel 3 is not.
            dsmr_extra_device_channel=DataloggerSettings.DSMR_EXTRA_DEVICE_CHANNEL_3,
        )

    def _dsmr_dummy_data(self):
        return [
            "/FLU5\253769484_A\r\n",
            "\r\n",
            "0-0:96.1.4(012345678901234567890123456789)\r\n",
            "0-0:96.1.1(012345678901234567890123456789)\r\n",
            "0-0:1.0.0(230119124638W)\r\n",
            "1-0:1.8.1(004423.770*kWh)\r\n",
            "1-0:1.8.2(002607.237*kWh)\r\n",
            "1-0:2.8.1(001194.693*kWh)\r\n",
            "1-0:2.8.2(000755.554*kWh)\r\n",
            "0-0:96.14.0(0001)\r\n",
            "1-0:1.4.0(00.000*kW)\r\n",
            "1-0:1.6.0(230116090000W)(11.173*kW)\r\n",
            "0-0:98.1.0(1)(1-0:1.6.0)(1-0:1.6.0)(230101000000W)(221230114500W)(13.603*kW)\r\n",
            "1-0:1.7.0(00.000*kW)\r\n",
            "1-0:2.7.0(00.204*kW)\r\n",
            "1-0:21.7.0(00.000*kW)\r\n",
            "1-0:41.7.0(00.177*kW)\r\n",
            "1-0:61.7.0(00.109*kW)\r\n",
            "1-0:22.7.0(00.491*kW)\r\n",
            "1-0:42.7.0(00.000*kW)\r\n",
            "1-0:62.7.0(00.000*kW)\r\n",
            "1-0:32.7.0(234.3*V)\r\n",
            "1-0:52.7.0(234.2*V)\r\n",
            "1-0:72.7.0(234.3*V)\r\n",
            "1-0:31.7.0(002.18*A)\r\n",
            "1-0:51.7.0(000.93*A)\r\n",
            "1-0:71.7.0(000.60*A)\r\n",
            "0-0:96.3.10(1)\r\n",
            "0-0:17.0.0(999.9*kW)\r\n",
            "1-0:31.4.0(999*A)\r\n",
            "0-0:96.13.0()\r\n",
            # Active gas device
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.1(012345678901234567890123456789)\r\n",
            "0-1:24.4.0(1)\r\n",
            "0-1:24.2.3(230119124616W)(00734.607*m3)\r\n",
            # Inactive/stale gas device
            "0-2:24.1.0(003)\r\n",
            "0-2:96.1.1(012345678901234567890123456789)\r\n",
            "0-2:24.4.0(1)\r\n",
            "0-2:24.2.3(230119124005W)(00000.000*m3)\r\n",
            "!B315",
        ]

    def test_reading_creation(self):
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_falls_back_to_available_channel(self):
        self._fake_dsmr_reading()
        reading = DsmrReading.objects.get()

        # Channel 3 was configured but isn't in the telegram, so the fallback (last available
        # MBus channel, here channel 2) is used instead of leaving the extra device data empty.
        self.assertIsNotNone(reading.extra_device_timestamp)
        self.assertEqual(
            reading.extra_device_timestamp,
            datetime(2023, 1, 19, 11, 40, 5, tzinfo=ZoneInfo("UTC")),
        )
        self.assertEqual(reading.extra_device_delivered, Decimal("0.000"))
