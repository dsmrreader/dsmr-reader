from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from zoneinfo import ZoneInfo

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestDatalogger(FakeDsmrReadingMixin, TestCase):
    """Belgium Fluvius telegram with a gas (type 3) and a water (type 7) meter on MBus channels 1 and 2.

    The water meter reports a newer timestamp than the gas meter. The gas reading must be used regardless.
    """

    def setUp(self):
        DataloggerSettings.get_solo()
        DataloggerSettings.objects.all().update(dsmr_version=DataloggerSettings.DSMR_BELGIUM_FLUVIUS)

    def _dsmr_dummy_data(self):
        return [
            "/FLU5\\253770234_A\r\n",
            "\r\n",
            "0-0:96.1.4(50217)\r\n",
            "0-0:96.1.1(3153414731313030303339313932)\r\n",
            "0-0:1.0.0(261026190733W)\r\n",
            "1-0:1.8.1(011461.194*kWh)\r\n",
            "1-0:1.8.2(014044.655*kWh)\r\n",
            "1-0:2.8.1(005982.412*kWh)\r\n",
            "1-0:2.8.2(002349.595*kWh)\r\n",
            "0-0:96.14.0(0001)\r\n",
            "1-0:1.4.0(00.346*kW)\r\n",
            "1-0:1.6.0(261001103000S)(03.668*kW)\r\n",
            "0-0:98.1.0(13)(1-0:1.6.0)(1-0:1.6.0)(251001000000S)(250929174500S)(07.030*kW)(251101000000W)(251026104500W)(03.677*kW)(251201000000W)(251113081500W)(03.304*kW)(260101000000W)(251207193000W)(04.626*kW)(260201000000W)(260111214500W)(07.395*kW)(260301000000W)(260206183000W)(03.980*kW)(260401000000S)(260317081500W)(02.925*kW)(260501000000S)(260418174500S)(03.951*kW)(260601000000S)(260530193000S)(05.616*kW)(260701000000S)(260628103000S)(07.220*kW)(260801000000S)(260714093000S)(02.609*kW)(260901000000S)(260815104500S)(05.569*kW)(261001000000S)(260928173000S)(03.882*kW)\r\n",
            "1-0:1.7.0(01.357*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "1-0:21.7.0(01.357*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "1-0:32.7.0(227.1*V)\r\n",
            "1-0:31.7.0(006.45*A)\r\n",
            "0-0:96.3.10(1)\r\n",
            "0-0:17.0.0(999.9*kW)\r\n",
            "1-0:31.4.0(999*A)\r\n",
            "0-0:96.13.0()\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.1(5445535447415330303030303031)\r\n",
            "0-1:24.4.0(1)\r\n",
            "0-1:24.2.3(261026190501W)(11247.060*m3)\r\n",
            "0-2:24.1.0(007)\r\n",
            "0-2:96.1.1(5445535457415445523030303031)\r\n",
            "0-2:24.2.1(261026190527W)(00156.741*m3)\r\n",
            "!5B3A",
        ]

    def test_gas_reading_used_instead_of_newer_water_reading(self):
        self._fake_dsmr_reading()
        reading = DsmrReading.objects.get()

        self.assertEqual(reading.extra_device_delivered, Decimal("11247.060"))
        self.assertEqual(reading.extra_device_timestamp, datetime(2026, 10, 26, 18, 5, 1, tzinfo=ZoneInfo("UTC")))
