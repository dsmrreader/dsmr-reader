from decimal import Decimal
from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.statistics import MeterStatistics
import dsmr_consumption.services


class TestServices(InterceptStdoutMixin, TestCase):
    fixtures = ['dsmr_consumption/test_dsmrreading.json', 'dsmr_consumption/test_energysupplierprice.json']
    support_gas_readings = None
    support_prices = None

    def setUp(self):
        self.support_gas_readings = True
        self.support_prices = True
        self.assertEqual(DsmrReading.objects.all().count(), 3)
        MeterStatistics.get_solo()
        MeterStatistics.objects.all().update(dsmr_version='42')

        if self.support_gas_readings:
            self.assertTrue(DsmrReading.objects.unprocessed().exists())
        else:
            self.assertFalse(DsmrReading.objects.unprocessed().exists())

        ConsumptionSettings.get_solo()

    def test_processing(self):
        """ Test fixed data parse outcome. """
        # Default is grouping by minute, so make sure to revert that here.
        consumption_settings = ConsumptionSettings.get_solo()
        consumption_settings.compactor_grouping_type = ConsumptionSettings.COMPACTOR_GROUPING_BY_READING
        consumption_settings.save()

        self.assertFalse(
            ElectricityConsumption.objects.filter(
                phase_currently_delivered_l2__isnull=False,
                phase_currently_delivered_l3__isnull=False
            ).exists()
        )

        dsmr_consumption.services.compact_all()

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 3)

        if self.support_gas_readings:
            self.assertEqual(GasConsumption.objects.count(), 2)
            self.assertEqual(
                [x.read_at for x in GasConsumption.objects.all()],
                [
                    # Asume a one hour backtrack.
                    timezone.make_aware(timezone.datetime(2015, 11, 10, hour=18), timezone.utc),
                    timezone.make_aware(timezone.datetime(2015, 11, 10, hour=19), timezone.utc)
                ]
            )
        else:
            self.assertEqual(GasConsumption.objects.count(), 0)

        self.assertTrue(
            ElectricityConsumption.objects.filter(
                phase_currently_delivered_l2__isnull=False,
                phase_currently_delivered_l3__isnull=False
            ).exists()
        )

    def test_duplicate_processing(self):
        """ Duplicate readings should not crash the compactor when not grouping. """
        # Default is grouping by minute, so make sure to revert that here.
        consumption_settings = ConsumptionSettings.get_solo()
        consumption_settings.compactor_grouping_type = ConsumptionSettings.COMPACTOR_GROUPING_BY_READING
        consumption_settings.save()

        # Just duplicate one, as it will cause: IntegrityError UNIQUE constraint failed: ElectricityConsumption.read_at
        duplicate_reading = DsmrReading.objects.all()[0]
        duplicate_reading.pk = None
        duplicate_reading.electricity_currently_delivered *= 2  # Make it differ.
        duplicate_reading.save()

        dsmr_consumption.services.compact_all()

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 3)

        if self.support_gas_readings:
            self.assertEqual(GasConsumption.objects.count(), 2)
        else:
            self.assertEqual(GasConsumption.objects.count(), 0)

    @mock.patch('django.utils.timezone.now')
    def test_grouping(self, now_mock):
        """ Test grouping per minute, instead of the default 10-second interval. """

        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2015, 11, 10, hour=21)
        )

        # Make sure to verify the blocking of read ahead.
        dr = DsmrReading.objects.get(pk=3)
        dr.timestamp = timezone.now()
        dr.save()

        dsmr_consumption.services.compact_all()

        self.assertEqual(DsmrReading.objects.unprocessed().count(), 1)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 1)

        if self.support_gas_readings:
            self.assertEqual(GasConsumption.objects.count(), 1)
        else:
            self.assertEqual(GasConsumption.objects.count(), 0)

    def test_creation(self):
        """ Test the datalogger's builtin fallback for initial readings. """
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())

        dsmr_consumption.services.compact_all()

        self.assertTrue(ElectricityConsumption.objects.exists())

        if self.support_gas_readings:
            self.assertTrue(GasConsumption.objects.exists())
        else:
            self.assertFalse(GasConsumption.objects.exists())

    def test_day_consumption(self):
        with self.assertRaises(LookupError):
            dsmr_consumption.services.day_consumption(timezone.now() + timezone.timedelta(weeks=1))

        now = timezone.make_aware(timezone.datetime(2016, 1, 1, hour=13))
        ElectricityConsumption.objects.create(
            read_at=now,  # Now.
            delivered_1=1,
            returned_1=1.5,
            delivered_2=2,
            returned_2=2.5,
            currently_delivered=10,
            currently_returned=20,
        )
        ElectricityConsumption.objects.create(
            read_at=now + timezone.timedelta(hours=1),  # Next hour.
            delivered_1=1 + 1,
            returned_1=1 + 2,
            delivered_2=2 + 3,
            returned_2=2 + 4,
            currently_delivered=10 + 5,
            currently_returned=20 + 6,
        )
        ElectricityConsumption.objects.create(
            read_at=now + timezone.timedelta(days=1),  # Next day.
            delivered_1=2,
            returned_1=2,
            delivered_2=4,
            returned_2=4,
            currently_delivered=20,
            currently_returned=40,
        )

        data = dsmr_consumption.services.day_consumption(day=now)
        self.assertIsInstance(data, dict)
        self.assertEqual(data['electricity1'], 1)
        self.assertEqual(data['electricity1_returned'], Decimal('1.5'))
        self.assertEqual(data['electricity2'], 3)
        self.assertEqual(data['electricity2_returned'], Decimal('3.5'))
        self.assertEqual(data['electricity_merged'], 4)
        self.assertEqual(data['electricity_returned_merged'], 5)

        if self.support_prices:
            self.assertEqual(data['electricity1_cost'], Decimal('0.25'))
            self.assertEqual(data['electricity2_cost'], Decimal('0.75'))
            self.assertEqual(data['total_cost'], 1)
        else:
            self.assertEqual(data['electricity1_cost'], 0)
            self.assertEqual(data['electricity2_cost'], 0)
            self.assertEqual(data['total_cost'], 0)

        GasConsumption.objects.create(
            read_at=now,  # Now.
            delivered=100,
            currently_delivered=1,
        )
        GasConsumption.objects.create(
            read_at=now + timezone.timedelta(hours=1),  # Next hour.
            delivered=100 + 20,
            currently_delivered=1,
        )
        GasConsumption.objects.create(
            read_at=now + timezone.timedelta(days=1),  # Next day.
            delivered=200,
            currently_delivered=10,
        )

        data = dsmr_consumption.services.day_consumption(day=now)
        self.assertEqual(data['gas'], 20)

    def test_round_decimal(self):
        rounded = dsmr_consumption.services.round_decimal(decimal_price=1.555)
        self.assertIsInstance(rounded, Decimal)  # Should auto convert to decimal.
        self.assertEqual(rounded, Decimal('1.56'))

        rounded = dsmr_consumption.services.round_decimal(decimal_price=Decimal('1.555'))
        self.assertEqual(rounded, Decimal('1.56'))

    def test_calculate_slumber_consumption_watt(self):
        most_common = dsmr_consumption.services.calculate_slumber_consumption_watt()
        self.assertIsNone(most_common)

        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=1,
            returned_1=1,
            delivered_2=2,
            returned_2=2,
            currently_delivered=0.25,
            currently_returned=0,
        )
        ElectricityConsumption.objects.create(
            read_at=timezone.now() + timezone.timedelta(minutes=1),
            delivered_1=1,
            returned_1=1,
            delivered_2=2,
            returned_2=2,
            currently_delivered=0.25,
            currently_returned=0,
        )
        ElectricityConsumption.objects.create(
            read_at=timezone.now() + timezone.timedelta(minutes=2),
            delivered_1=1,
            returned_1=1,
            delivered_2=2,
            returned_2=2,
            currently_delivered=1,
            currently_returned=0,
        )
        most_common = dsmr_consumption.services.calculate_slumber_consumption_watt()

        # Average = 250 + 250 + 1000 / 3 = 500.
        self.assertEqual(most_common, 500)

    @mock.patch('django.utils.timezone.now')
    def test_calculate_min_max_consumption_watt(self, now_mock):
        now_mock.return_value = timezone.localtime(timezone.make_aware(
            timezone.datetime(2017, 1, 1, hour=12)
        ))

        result = dsmr_consumption.services.calculate_min_max_consumption_watt()
        self.assertNotIn('total_min', result)
        self.assertNotIn('total_max', result)

        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=0.25,
            currently_returned=0,
            phase_currently_delivered_l1=0.5,
        )
        ElectricityConsumption.objects.create(
            read_at=timezone.now() + timezone.timedelta(hours=24),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=1.35,
            currently_returned=0,
            phase_currently_delivered_l2=0.75,
        )
        ElectricityConsumption.objects.create(
            read_at=timezone.now() + timezone.timedelta(hours=48),
            delivered_1=0,
            returned_1=0,
            delivered_2=0,
            returned_2=0,
            currently_delivered=6.123,
            currently_returned=0,
            phase_currently_delivered_l3=1.5,
        )
        result = dsmr_consumption.services.calculate_min_max_consumption_watt()

        self.assertEqual(result['total_min'][0], 'Sunday January 1st, 2017')
        self.assertEqual(result['total_min'][1], 250)

        self.assertEqual(result['total_max'][0], 'Tuesday January 3rd, 2017')
        self.assertEqual(result['total_max'][1], 6123)

        self.assertEqual(result['l1_max'][0], 'Sunday January 1st, 2017')
        self.assertEqual(result['l1_max'][1], 500)

        self.assertEqual(result['l2_max'][0], 'Monday January 2nd, 2017')
        self.assertEqual(result['l2_max'][1], 750)

        self.assertEqual(result['l3_max'][0], 'Tuesday January 3rd, 2017')
        self.assertEqual(result['l3_max'][1], 1500)

    def test_clear_consumption(self):
        # Prepare some test data that should be deleted.
        ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=1,
            returned_1=1,
            delivered_2=2,
            returned_2=2,
            currently_delivered=0.25,
            currently_returned=0,
        )
        GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=100,
            currently_delivered=1,
        )

        self.assertTrue(ElectricityConsumption.objects.exists())
        self.assertTrue(GasConsumption.objects.exists())

        dsmr_consumption.services.clear_consumption()

        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())


class TestServicesDSMRv5(InterceptStdoutMixin, TestCase):
    """ Biggest difference is the interval of gas readings. """
    fixtures = ['dsmr_consumption/test_dsmrreading_v5.json', 'dsmr_consumption/test_energysupplierprice.json']

    def setUp(self):
        self.assertEqual(DsmrReading.objects.all().count(), 6)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        ConsumptionSettings.get_solo()
        MeterStatistics.get_solo()
        MeterStatistics.objects.all().update(dsmr_version='50')

    def test_processing_grouped(self):
        dsmr_consumption.services.compact_all()

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(GasConsumption.objects.count(), 4)
        self.assertEqual(
            [float(x.currently_delivered) for x in GasConsumption.objects.all()],
            [0.0, 0.05, 0.03, 0.07]
        )

    def test_processing_ungrouped(self):
        ConsumptionSettings.objects.update(compactor_grouping_type=ConsumptionSettings.COMPACTOR_GROUPING_BY_READING)

        dsmr_consumption.services.compact_all()

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(GasConsumption.objects.count(), 6)
        self.assertEqual(
            [float(x.currently_delivered) for x in GasConsumption.objects.all()],
            [0.0, 0.05, 0.01, 0.01, 0.01, 0.07]
        )


class TestServicesWithoutGas(TestServices):
    fixtures = ['dsmr_consumption/test_dsmrreading_without_gas.json', 'dsmr_consumption/test_energysupplierprice.json']

    def setUp(self):
        super(TestServicesWithoutGas, self).setUp()
        self.support_gas_readings = False


class TestServicesWithoutPrices(TestServices):
    fixtures = ['dsmr_consumption/test_dsmrreading.json']

    def setUp(self):
        super(TestServicesWithoutPrices, self).setUp()
        self.support_prices = False
