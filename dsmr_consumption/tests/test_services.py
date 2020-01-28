from decimal import Decimal
from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.statistics import MeterStatistics
import dsmr_consumption.services
from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class TestServices(InterceptStdoutMixin, TestCase):
    fixtures = [
        'dsmr_consumption/test_dsmrreading.json',
        'dsmr_consumption/test_energysupplierprice.json',
        'dsmr_consumption/test_statistics.json',
    ]
    support_gas_readings = None
    support_prices = None
    schedule_process = None

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

        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_GENERATE_CONSUMPTION)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

    def test_processing(self):
        """ Test fixed data parse outcome. """
        # Default is grouping by minute, so make sure to revert that here.
        consumption_settings = ConsumptionSettings.get_solo()
        consumption_settings.electricity_grouping_type = ConsumptionSettings.ELECTRICITY_GROUPING_BY_READING
        consumption_settings.save()

        self.assertFalse(
            ElectricityConsumption.objects.filter(
                phase_currently_delivered_l2__isnull=False,
                phase_currently_delivered_l3__isnull=False
            ).exists()
        )

        dsmr_consumption.services.run(self.schedule_process)

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
        consumption_settings.electricity_grouping_type = ConsumptionSettings.ELECTRICITY_GROUPING_BY_READING
        consumption_settings.save()

        # Just duplicate one, as it will cause: IntegrityError UNIQUE constraint failed: ElectricityConsumption.read_at
        duplicate_reading = DsmrReading.objects.all()[0]
        duplicate_reading.pk = None
        duplicate_reading.electricity_currently_delivered *= 2  # Make it differ.
        duplicate_reading.save()

        dsmr_consumption.services.run(self.schedule_process)

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 3)

        if self.support_gas_readings:
            self.assertEqual(GasConsumption.objects.count(), 2)
        else:
            self.assertEqual(GasConsumption.objects.count(), 0)

    @mock.patch('django.utils.timezone.now')
    def test_grouping(self, now_mock):
        """ Test grouping per minute, instead of the default X-second interval. """
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2015, 11, 10, hour=21)
        )

        # Make sure to verify the blocking of read ahead.
        dr = DsmrReading.objects.get(pk=3)
        dr.timestamp = timezone.now()
        dr.save()

        dsmr_consumption.services.run(self.schedule_process)

        self.assertEqual(DsmrReading.objects.unprocessed().count(), 1)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(ElectricityConsumption.objects.count(), 1)

        if self.support_gas_readings:
            self.assertEqual(GasConsumption.objects.count(), 1)
        else:
            self.assertEqual(GasConsumption.objects.count(), 0)

        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(seconds=15))  # 15 s delay

    @mock.patch('django.utils.timezone.now')
    def test_extra_device_existing_data(self, now_mock):
        """ Checks whether readings from the extra device are sorted correctly. """
        now_mock.return_value = DsmrReading.objects.all().order_by('-timestamp')[0].timestamp

        # Clear any gas data in reading.
        DsmrReading.objects.all().update(extra_device_delivered=0)

        # Default data for fields we do not care about.
        reading_kwargs = dict(
            electricity_delivered_1=0,
            electricity_returned_1=0,
            electricity_delivered_2=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )

        # Insert existing data.
        GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=75,
            currently_delivered=0
        )

        # Starting point. MUST be BEFORE the fixture's date (2015-11-10).
        default_reading_timestamp = timezone.now() - timezone.timedelta(weeks=52)

        # Add some data, mixed timestamps, not in default order.
        reading_timestamp = default_reading_timestamp
        DsmrReading.objects.create(
            timestamp=reading_timestamp,
            extra_device_timestamp=reading_timestamp,
            extra_device_delivered=3.0,
            **reading_kwargs
        )
        reading_timestamp = default_reading_timestamp - timezone.timedelta(hours=2)  # Earlier
        DsmrReading.objects.create(
            timestamp=reading_timestamp,
            extra_device_timestamp=reading_timestamp,
            extra_device_delivered=2.0,
            **reading_kwargs
        )
        reading_timestamp = default_reading_timestamp - timezone.timedelta(hours=3)  # Earlier as well
        DsmrReading.objects.create(
            timestamp=reading_timestamp,
            extra_device_timestamp=reading_timestamp,
            extra_device_delivered=1.0,
            **reading_kwargs
        )
        reading_timestamp = default_reading_timestamp + timezone.timedelta(hours=1)  # Later than first one
        DsmrReading.objects.create(
            timestamp=reading_timestamp,
            extra_device_timestamp=reading_timestamp,
            extra_device_delivered=4.0,
            **reading_kwargs
        )
        reading_timestamp = default_reading_timestamp + timezone.timedelta(hours=2)
        DsmrReading.objects.create(
            timestamp=reading_timestamp,
            extra_device_timestamp=reading_timestamp,
            extra_device_delivered=5.0,
            **reading_kwargs
        )

        dsmr_consumption.services.run(self.schedule_process)

        # This should not happen anymore.
        self.assertFalse(GasConsumption.objects.filter(currently_delivered__lt=0).exists())

        # At least one should contain a value now.
        self.assertTrue(GasConsumption.objects.filter(currently_delivered__gt=0).exists())

    @mock.patch('django.utils.timezone.now')
    def test_grouping_timing_bug(self, now_mock):
        """ #513: Using the system time instead of telegram time, might ignore some readings. """
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2018, 1, 1, hour=0, minute=0, second=0)
        )
        ElectricityConsumption.objects.all().delete()
        DsmrReading.objects.all().delete()
        reading_timestamp = timezone.now()
        DsmrReading.objects.create(
            timestamp=reading_timestamp + timezone.timedelta(seconds=15),
            electricity_delivered_1=1,
            electricity_returned_1=0,
            electricity_delivered_2=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )
        DsmrReading.objects.create(
            timestamp=reading_timestamp + timezone.timedelta(seconds=30),
            electricity_delivered_1=2,
            electricity_returned_1=0,
            electricity_delivered_2=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )

        # This should do nothing, minute is not passed yet.
        self.assertFalse(ElectricityConsumption.objects.exists())
        dsmr_consumption.services.run(self.schedule_process)
        self.assertFalse(ElectricityConsumption.objects.exists())

        # Pass minute. Fix should keep reading unprocessed.
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1, hour=0, minute=1, second=10))
        dsmr_consumption.services.run(self.schedule_process)
        self.assertFalse(ElectricityConsumption.objects.exists())

        # Add afterwards in passed minute. It should still be ignored.
        DsmrReading.objects.create(
            timestamp=reading_timestamp + timezone.timedelta(seconds=45),
            electricity_delivered_1=3,
            electricity_returned_1=0,
            electricity_delivered_2=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )
        dsmr_consumption.services.run(self.schedule_process)
        self.assertFalse(ElectricityConsumption.objects.exists())

        # Now create a new reading in the next minute, it should finally trigger the grouping, as desired.
        DsmrReading.objects.create(
            timestamp=reading_timestamp + timezone.timedelta(seconds=60),
            electricity_delivered_1=10,
            electricity_returned_1=0,
            electricity_delivered_2=0,
            electricity_returned_2=0,
            electricity_currently_delivered=0,
            electricity_currently_returned=0,
        )
        dsmr_consumption.services.run(self.schedule_process)
        self.assertTrue(ElectricityConsumption.objects.exists())

        # Check result, should be max of all three readings.
        self.assertTrue(ElectricityConsumption.objects.filter(delivered_1=3).exists())

    def test_creation(self):
        """ Test the datalogger's builtin fallback for initial readings. """
        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())

        dsmr_consumption.services.run(self.schedule_process)

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

            self.assertEqual(data['energy_supplier_price_electricity_delivered_1'], 1)
            self.assertEqual(data['energy_supplier_price_electricity_delivered_2'], 2)
            self.assertEqual(data['energy_supplier_price_electricity_returned_1'], 0.5)
            self.assertEqual(data['energy_supplier_price_electricity_returned_2'], 1.5)
            self.assertEqual(data['energy_supplier_price_gas'], 5)
        else:
            self.assertEqual(data['electricity1_cost'], 0)
            self.assertEqual(data['electricity2_cost'], 0)
            self.assertEqual(data['total_cost'], 0)

            self.assertEqual(data['energy_supplier_price_electricity_delivered_1'], 0)
            self.assertEqual(data['energy_supplier_price_electricity_delivered_2'], 0)
            self.assertEqual(data['energy_supplier_price_electricity_returned_1'], 0)
            self.assertEqual(data['energy_supplier_price_electricity_returned_2'], 0)
            self.assertEqual(data['energy_supplier_price_gas'], 0)

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

    @mock.patch('django.utils.timezone.now')
    def test_summarize_energy_contracts(self, now_mock):
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2017, 1, 2)
        )

        # Fetch inside our expected range.
        energy_contracts = dsmr_consumption.services.summarize_energy_contracts()

        if not EnergySupplierPrice.objects.exists():
            return self.assertEqual(len(energy_contracts), 0)

        summary = energy_contracts[0]['summary']

        self.assertEqual(summary['electricity1'], Decimal('2.732'))
        self.assertEqual(summary['electricity1_cost'], Decimal('0.57'))
        self.assertEqual(summary['electricity1_returned'], Decimal('0.000'))
        self.assertEqual(summary['electricity2'], Decimal('0.549'))
        self.assertEqual(summary['electricity2_cost'], Decimal('0.12'))
        self.assertEqual(summary['electricity2_returned'], Decimal('0.000'))
        self.assertEqual(summary['electricity_merged'], Decimal('3.281'))
        self.assertEqual(summary['electricity_cost_merged'], Decimal('0.69'))
        self.assertEqual(summary['electricity_returned_merged'], Decimal('0.000'))
        self.assertEqual(summary['gas'], Decimal('6.116'))
        self.assertEqual(summary['gas_cost'], Decimal('3.60'))
        self.assertEqual(summary['total_cost'], Decimal('4.29'))


class TestServicesDSMRv5(InterceptStdoutMixin, TestCase):
    """ Biggest difference is the interval of gas readings. """
    fixtures = ['dsmr_consumption/test_dsmrreading_v5.json', 'dsmr_consumption/test_energysupplierprice.json']
    schedule_process = None

    def setUp(self):
        self.assertEqual(DsmrReading.objects.all().count(), 7)
        self.assertTrue(DsmrReading.objects.unprocessed().exists())
        ConsumptionSettings.get_solo()
        MeterStatistics.get_solo()
        MeterStatistics.objects.all().update(dsmr_version='50')

        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_GENERATE_CONSUMPTION)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

    def test_processing_grouped(self):
        ConsumptionSettings.objects.update(gas_grouping_type=ConsumptionSettings.GAS_GROUPING_BY_HOUR)
        self.assertFalse(DsmrReading.objects.processed().exists())
        self.assertEqual(DsmrReading.objects.unprocessed().count(), 7)

        dsmr_consumption.services.run(self.schedule_process)

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertEqual(DsmrReading.objects.unprocessed().count(), 1)
        self.assertEqual(GasConsumption.objects.count(), 2)
        self.assertEqual(
            [float(x.currently_delivered) for x in GasConsumption.objects.all()],
            [0.0, 0.15]
        )

    def test_processing_ungrouped(self):
        ConsumptionSettings.objects.update(
            electricity_grouping_type=ConsumptionSettings.ELECTRICITY_GROUPING_BY_READING,
            gas_grouping_type=ConsumptionSettings.GAS_GROUPING_BY_CHANGE,
        )

        dsmr_consumption.services.run(self.schedule_process)

        self.assertTrue(DsmrReading.objects.processed().exists())
        self.assertFalse(DsmrReading.objects.unprocessed().exists())
        self.assertEqual(GasConsumption.objects.count(), 7)
        self.assertEqual(
            [float(x.currently_delivered) for x in GasConsumption.objects.all()],
            [0.0, 0.05, 0.01, 0.01, 0.01, 0.07, 0.00]
        )


class TestServicesWithoutGas(TestServices):
    fixtures = [
        'dsmr_consumption/test_dsmrreading_without_gas.json',
        'dsmr_consumption/test_energysupplierprice.json',
        'dsmr_consumption/test_statistics.json',
    ]

    def setUp(self):
        super(TestServicesWithoutGas, self).setUp()
        self.support_gas_readings = False


class TestServicesWithoutPrices(TestServices):
    fixtures = ['dsmr_consumption/test_dsmrreading.json', 'dsmr_consumption/test_statistics.json']

    def setUp(self):
        super(TestServicesWithoutPrices, self).setUp()
        self.support_prices = False
