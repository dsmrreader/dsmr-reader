from unittest import mock

from django.utils import timezone

from dsmr_api.tests.v2 import APIv2TestCase
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_consumption.models.consumption import GasConsumption


class TestToday(APIv2TestCase):
    fixtures = ['dsmr_api/test_electricity_consumption.json']

    @mock.patch('django.utils.timezone.now')
    def test_get(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))

        # No data.
        result = self._request('today-consumption')
        self.assertEqual(result, 'No electricity readings found for: 2017-01-01')

        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 12, hour=12))
        result = self._request('today-consumption')

        self.assertEqual(result['day'], '2015-12-12')

        FIELDS = (
            'day', 'electricity1', 'electricity2', 'electricity1_returned', 'electricity2_returned',
            'electricity1_cost', 'electricity2_cost', 'gas', 'gas_cost', 'total_cost', 'electricity_merged',
            'electricity_returned_merged'
        )

        for x in FIELDS:
            self.assertIn(x, result.keys())

        # It's also tested in the service used for fetching the data, but w/e...
        self.assertEqual(result['electricity_merged'], result['electricity1'] + result['electricity2'])
        self.assertEqual(
            result['electricity_returned_merged'], result['electricity1_returned'] + result['electricity2_returned']
        )


class TestTodayWithGas(TestToday):
    fixtures = [
        'dsmr_api/test_electricity_consumption.json',
        'dsmr_api/test_electricity_consumption.json',
        'dsmr_api/test_gas_consumption.json'
    ]


class ElectricityLive(APIv2TestCase):
    fixtures = ['dsmr_api/test_dsmrreading.json']

    @mock.patch('django.utils.timezone.now')
    def test_get(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 7, 2))

        # Without prices.
        result = self._request('electricity-live')
        self.assertEqual(result['timestamp'], '2016-07-01T22:00:00+02:00')
        self.assertEqual(result['currently_returned'], 123)
        self.assertEqual(result['currently_delivered'], 1123)

        # Now with prices.
        EnergySupplierPrice.objects.create(
            start=timezone.now().date(),
            end=(timezone.now() + timezone.timedelta(hours=24)).date(),
            electricity_delivered_1_price=0.010,
            electricity_delivered_2_price=0.020,
        )
        MeterStatistics.objects.update(electricity_tariff=1)

        result = self._request('electricity-live')
        self.assertEqual(result['timestamp'], '2016-07-01T22:00:00+02:00')
        self.assertEqual(result['currently_returned'], 123)
        self.assertEqual(result['currently_delivered'], 1123)
        self.assertEqual(result['cost_per_hour'], '0.01')


class GasLive(APIv2TestCase):
    @mock.patch('django.db.models.signals.post_save.send')  # Disable signals for side effects.
    @mock.patch('django.utils.timezone.now')
    def test_get(self, now_mock, *mocks):
        # Without gas.
        result = self._request('gas-live')
        self.assertEqual(result, {})

        now_mock.return_value = timezone.make_aware(timezone.datetime(2019, 4, 20))
        GasConsumption.objects.create(**{
            "read_at": "2019-04-19T12:00:00+02:00",
            "delivered": "123.456",
            "currently_delivered": "0.000"
        })
        GasConsumption.objects.create(**{
            "read_at": "2019-04-19T13:00:00+02:00",
            "delivered": "125.000",
            "currently_delivered": "1.544"
        })

        # Without prices.
        result = self._request('gas-live')
        self.assertEqual(result['timestamp'], '2019-04-19T13:00:00+02:00')
        self.assertEqual(result['currently_delivered'], 1.544)

        # Now with prices.
        EnergySupplierPrice.objects.create(
            start=timezone.now().date(),
            end=(timezone.now() + timezone.timedelta(hours=24)).date(),
            gas_price=0.50,
        )

        result = self._request('gas-live')
        self.assertEqual(result['timestamp'], '2019-04-19T13:00:00+02:00')
        self.assertEqual(result['currently_delivered'], 1.544)
        self.assertEqual(result['cost_per_interval'], '0.77')


class TestEnergySupplierPrice(APIv2TestCase):
    fixtures = ['dsmr_api/test_energysupplierprice.json']

    def test_get(self):
        resultset = self._request('energy-supplier-price', data={'limit': 10})
        self.assertEqual(resultset['count'], 2)
        self.assertEqual(len(resultset['results']), 2)
        self.assertEqual(resultset['results'][0]['id'], 1)
        self.assertEqual(resultset['results'][1]['id'], 2)

        # Data. For some reason all decimals have +1 precision.
        self.assertEqual(resultset['results'][0]['start'], '2015-01-01')
        self.assertEqual(resultset['results'][0]['end'], '2018-01-01')
        self.assertEqual(resultset['results'][0]['description'], 'Test')
        self.assertEqual(resultset['results'][0]['electricity_delivered_1_price'], '1.000000')
        self.assertEqual(resultset['results'][0]['electricity_delivered_2_price'], '2.000000')
        self.assertEqual(resultset['results'][0]['gas_price'], '5.000000')
        self.assertEqual(resultset['results'][0]['electricity_returned_1_price'], '0.500000')
        self.assertEqual(resultset['results'][0]['electricity_returned_2_price'], '1.500000')
        self.assertEqual(resultset['results'][0]['fixed_daily_cost'], '1.234560')

        # Limit.
        resultset = self._request('energy-supplier-price', data={'limit': 1})
        self.assertEqual(resultset['count'], 2)
        self.assertEqual(len(resultset['results']), 1)

        # Sort.
        resultset = self._request('energy-supplier-price', data={'ordering': '-start', 'limit': 10})
        self.assertEqual(resultset['count'], 2)
        self.assertEqual(resultset['results'][0]['id'], 2)
        self.assertEqual(resultset['results'][1]['id'], 1)

        # Search
        resultset = self._request('energy-supplier-price', data={'start__gte': '2017-12-12'})
        self.assertEqual(resultset['count'], 1)
        self.assertEqual(resultset['results'][0]['id'], 2)

        resultset = self._request('energy-supplier-price', data={'start__lte': '2017-12-12'})
        self.assertEqual(resultset['count'], 1)
        self.assertEqual(resultset['results'][0]['id'], 1)


class TestElectricity(APIv2TestCase):
    fixtures = ['dsmr_api/test_electricity_consumption.json']

    def test_get(self):
        resultset = self._request('electricity-consumption', data={'limit': 100})
        self.assertEqual(resultset['count'], 67)
        self.assertEqual(resultset['results'][0]['id'], 95)
        self.assertEqual(resultset['results'][1]['id'], 96)
        self.assertEqual(resultset['results'][65]['id'], 217)
        self.assertEqual(resultset['results'][66]['id'], 218)

        # Limit.
        resultset = self._request('electricity-consumption', data={'limit': 10})
        self.assertEqual(resultset['count'], 67)
        self.assertEqual(len(resultset['results']), 10)

        # Sort.
        resultset = self._request('electricity-consumption', data={'ordering': '-read_at', 'limit': 100})
        self.assertEqual(resultset['count'], 67)
        self.assertEqual(resultset['results'][0]['id'], 218)
        self.assertEqual(resultset['results'][1]['id'], 217)
        self.assertEqual(resultset['results'][65]['id'], 96)
        self.assertEqual(resultset['results'][66]['id'], 95)

        # Search
        resultset = self._request('electricity-consumption', data={'read_at__gte': '2015-12-12 02:00:00'})  # Z+01:00
        self.assertEqual(resultset['count'], 4)
        self.assertEqual(resultset['results'][0]['id'], 215)
        self.assertEqual(resultset['results'][1]['id'], 216)
        self.assertEqual(resultset['results'][2]['id'], 217)
        self.assertEqual(resultset['results'][3]['id'], 218)

        resultset = self._request('electricity-consumption', data={'read_at__lte': '2015-12-12 02:00:00', 'limit': 100})
        self.assertEqual(resultset['count'], 64)
        self.assertEqual(resultset['results'][0]['id'], 95)
        self.assertEqual(resultset['results'][1]['id'], 96)


class TestGas(APIv2TestCase):
    fixtures = ['dsmr_api/test_gas_consumption.json']

    def test_get(self):
        resultset = self._request('gas-consumption', data={'limit': 100})
        self.assertEqual(resultset['count'], 31)
        self.assertEqual(resultset['results'][0]['id'], 1)
        self.assertEqual(resultset['results'][1]['id'], 2)
        self.assertEqual(resultset['results'][29]['id'], 30)
        self.assertEqual(resultset['results'][30]['id'], 31)

        # Limit.
        resultset = self._request('gas-consumption', data={'limit': 10})
        self.assertEqual(resultset['count'], 31)
        self.assertEqual(len(resultset['results']), 10)

        # Sort.
        resultset = self._request('gas-consumption', data={'ordering': '-read_at', 'limit': 100})
        self.assertEqual(resultset['count'], 31)
        self.assertEqual(resultset['results'][0]['id'], 31)
        self.assertEqual(resultset['results'][1]['id'], 30)
        self.assertEqual(resultset['results'][29]['id'], 2)
        self.assertEqual(resultset['results'][30]['id'], 1)

        # Search
        resultset = self._request('gas-consumption', data={'read_at__gte': '2015-12-13 00:00:00'})  # Z+01:00
        self.assertEqual(resultset['count'], 4)
        self.assertEqual(resultset['results'][0]['id'], 28)
        self.assertEqual(resultset['results'][1]['id'], 29)
        self.assertEqual(resultset['results'][2]['id'], 30)
        self.assertEqual(resultset['results'][3]['id'], 31)

        resultset = self._request('gas-consumption', data={'read_at__lte': '2015-12-13 00:00:00', 'limit': 100})
        self.assertEqual(resultset['count'], 28)
        self.assertEqual(resultset['results'][0]['id'], 1)
        self.assertEqual(resultset['results'][1]['id'], 2)
