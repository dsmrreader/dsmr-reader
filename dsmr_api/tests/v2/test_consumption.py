from unittest import mock

from django.utils import timezone

from dsmr_api.tests.v2 import APIv2TestCase
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.statistics import MeterStatistics


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
            'electricity1_cost', 'electricity2_cost', 'gas', 'gas_cost', 'total_cost'
        )

        for x in FIELDS:
            self.assertIn(x, result.keys())


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
        self.assertEqual(result['timestamp'], '2016-07-01T20:00:00Z')
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
        self.assertEqual(result['timestamp'], '2016-07-01T20:00:00Z')
        self.assertEqual(result['currently_returned'], 123)
        self.assertEqual(result['currently_delivered'], 1123)
        self.assertEqual(result['cost_per_hour'], '0.02')


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
