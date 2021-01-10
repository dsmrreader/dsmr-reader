from datetime import datetime
from decimal import Decimal
from unittest import mock

from django.test import TestCase
import pytz

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.tests.datalogger.mixins import FakeDsmrReadingMixin


class TestSerial(FakeDsmrReadingMixin, InterceptCommandStdoutMixin, TestCase):
    """ Test example from Netbeheer docs. """

    def _dsmr_dummy_data(self):
        return [
            "/ISk5\2MT382-1000\r\n",
            "\r\n",
            "1-3:0.2.8(50)\r\n",
            "0-0:1.0.0(101209113020W)\r\n",
            "0-0:96.1.1(4B384547303034303436333935353037)\r\n",
            "1-0:1.8.1(123456.789*kWh)\r\n",
            "1-0:1.8.2(123456.789*kWh)\r\n",
            "1-0:2.8.1(123456.789*kWh)\r\n",
            "1-0:2.8.2(123456.789*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(01.193*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00004)\r\n",
            "0-0:96.7.9(00002)\r\n",
            "1-0:99.97.0(2)(0-0:96.7.19)(101208152415W)(0000000240*s)(101208151004W)(0000000301*s)\r\n",
            "1-0:32.32.0(00002)\r\n",
            "1-0:52.32.0(00001)\r\n",
            "1-0:72.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "1-0:52.36.0(00003)\r\n",
            "1-0:72.36.0(00000)\r\n",
            "0-0:96.13.0(303132333435363738393A3B3C3D3E3F303132333435363738393A3B3C3D3E3F303132333435363738393A3B3C3D3E"
            "3F303132333435363738393A3B3C3D3E3F303132333435363738393A3B3C3D3E3F)\r\n",
            "1-0:32.7.0(220.1*V)\r\n",
            "1-0:52.7.0(220.2*V)\r\n",
            "1-0:72.7.0(220.3*V)\r\n",
            "1-0:31.7.0(001*A)\r\n",
            "1-0:51.7.0(002*A)\r\n",
            "1-0:71.7.0(003*A)\r\n",
            "1-0:21.7.0(01.111*kW)\r\n",
            "1-0:41.7.0(02.222*kW)\r\n",
            "1-0:61.7.0(03.333*kW)\r\n",
            "1-0:22.7.0(04.444*kW)\r\n",
            "1-0:42.7.0(05.555*kW)\r\n",
            "1-0:62.7.0(06.666*kW)\r\n",
            "0-1:24.1.0(003)\r\n",
            "0-1:96.1.0(3232323241424344313233343536373839)\r\n",
            "0-1:24.2.1(101209112500W)(12785.123*m3)\r\n",
            "!C2AA\n",  # Recalculated, seems wrong in docs?
        ]

    def test_reading_creation(self):
        self.assertFalse(DsmrReading.objects.exists())
        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())

    def test_reading_values(self):
        DataloggerSettings.get_solo()

        self._fake_dsmr_reading()
        self.assertTrue(DsmrReading.objects.exists())
        reading = DsmrReading.objects.get()
        self.assertEqual(reading.timestamp, datetime(2010, 12, 9, 10, 30, 20, tzinfo=pytz.UTC))
        self.assertEqual(reading.electricity_delivered_1, Decimal('123456.789'))
        self.assertEqual(reading.electricity_returned_1, Decimal('123456.789'))
        self.assertEqual(reading.electricity_delivered_2, Decimal('123456.789'))
        self.assertEqual(reading.electricity_returned_2, Decimal('123456.789'))
        self.assertEqual(reading.electricity_currently_delivered, Decimal('1.193'))
        self.assertEqual(reading.electricity_currently_returned, Decimal('0'))
        self.assertEqual(reading.extra_device_timestamp, datetime(2010, 12, 9, 10, 25, tzinfo=pytz.UTC))
        self.assertEqual(reading.extra_device_delivered, Decimal('12785.123'))
        self.assertEqual(reading.phase_currently_delivered_l1, Decimal('1.111'))
        self.assertEqual(reading.phase_currently_delivered_l2, Decimal('2.222'))
        self.assertEqual(reading.phase_currently_delivered_l3, Decimal('3.333'))
        self.assertEqual(reading.phase_currently_returned_l1, Decimal('4.444'))
        self.assertEqual(reading.phase_currently_returned_l2, Decimal('5.555'))
        self.assertEqual(reading.phase_currently_returned_l3, Decimal('6.666'))
        self.assertEqual(reading.phase_voltage_l1, Decimal('220.1'))
        self.assertEqual(reading.phase_voltage_l2, Decimal('220.2'))
        self.assertEqual(reading.phase_voltage_l3, Decimal('220.3'))
        self.assertEqual(reading.phase_power_current_l1, 1)
        self.assertEqual(reading.phase_power_current_l2, 2)
        self.assertEqual(reading.phase_power_current_l3, 3)

        meter_statistics = MeterStatistics.get_solo()
        self.assertEqual(meter_statistics.dsmr_version, '50')
        self.assertEqual(meter_statistics.electricity_tariff, 2)
        self.assertEqual(meter_statistics.power_failure_count, 4)
        self.assertEqual(meter_statistics.long_power_failure_count, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l1, 2)
        self.assertEqual(meter_statistics.voltage_sag_count_l2, 1)
        self.assertEqual(meter_statistics.voltage_sag_count_l3, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l1, 0)
        self.assertEqual(meter_statistics.voltage_swell_count_l2, 3)
        self.assertEqual(meter_statistics.voltage_swell_count_l3, 0)

    @mock.patch('django.utils.timezone.now')
    def test_telegram_override_timestamp(self, now_mock):
        """ Tests whether this user setting overrides as expectedly. """
        reading = self._reading_with_override_telegram_timestamp_active(now_mock)

        self.assertEqual(
            # CET > UTC. Minute marker rounded to 5 mins.
            reading.extra_device_timestamp, datetime(2021, 1, 15, 11, 30, 0, 0, tzinfo=pytz.UTC)
        )
