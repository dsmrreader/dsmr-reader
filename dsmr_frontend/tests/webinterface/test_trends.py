from unittest import mock
import json

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import DayStatistics


class TestViews(TestCase):
    """ Test whether views render at all. """
    fixtures = [
        'dsmr_frontend/test_dsmrreading.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/test_energysupplierprice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
        'dsmr_frontend/test_electricity_consumption.json',
        'dsmr_frontend/test_gas_consumption.json',
    ]
    namespace = 'frontend'
    support_data = True
    support_gas = True
    request_params = None

    def setUp(self):
        self.client = Client()
        self.request_params = dict(
            start_date='2016-01-01',
            end_date='2021-01-01',
        )

    def test_trends(self):
        response = self.client.get(
            reverse('{}:trends'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn('capabilities', response.context)
        self.assertIn('frontend_settings', response.context)

    def test_trends_xhr_bad_request(self):
        response = self.client.get(
            reverse('{}:trends-xhr-avg-consumption'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            reverse('{}:trends-xhr-consumption-by-tariff'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 400)

        response = self.client.get(
            reverse('{}:trends-xhr-consumption-by-tariff'.format(self.namespace)),
            dict(
                # Start cannot be before end
                start_date='2021-01-01',
                end_date='2016-01-01',
            )
        )
        self.assertEqual(response.status_code, 400)

    @mock.patch('django.utils.timezone.now')
    def test_trends_xhr_avg_consumption(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        response = self.client.get(
            reverse('{}:trends-xhr-avg-consumption'.format(self.namespace)),
            self.request_params
        )
        self.assertEqual(response.status_code, 200, response.content)
        json_response = json.loads(response.content.decode("utf-8"))

        if not self.support_data:
            return self.assertEqual(json_response, {"electricity": [], "electricity_returned": [], "gas": []})

        self.assertEqual(len(json_response['electricity']), 24)
        self.assertEqual(len(json_response['electricity_returned']), 24)

        if self.support_gas:
            self.assertEqual(len(json_response['gas']), 24)
        else:
            self.assertEqual(len(json_response['gas']), 0)

        # Test with missing electricity returned.
        ElectricityConsumption.objects.all().update(currently_returned=0)

        response = self.client.get(
            reverse('{}:trends-xhr-avg-consumption'.format(self.namespace)),
            self.request_params
        )
        json_response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(len(json_response['electricity_returned']), 0)

    @mock.patch('django.utils.timezone.now')
    def test_trends_xhr_by_tariff(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        response = self.client.get(
            reverse('{}:trends-xhr-consumption-by-tariff'.format(self.namespace)),
            self.request_params
        )
        self.assertEqual(response.status_code, 200, response.content)
        json_response = json.loads(response.content.decode("utf-8"))

        if not self.support_data:
            return self.assertEqual(json_response, {})

        self.assertIn('data', json_response)
        self.assertIn({'value': 84, 'name': 'Laagtarief'}, json_response['data'])
        self.assertIn({'value': 16, 'name': 'Hoogtarief'}, json_response['data'])

        # Test with no stats available (yet).
        DayStatistics.objects.all().delete()
        response = self.client.get(
            reverse('{}:trends-xhr-consumption-by-tariff'.format(self.namespace)),
            self.request_params
        )
        self.assertEqual(response.status_code, 200, response.content)


class TestViewsWithoutData(TestViews):
    """ Same tests as above, but without any data as it's flushed in setUp().  """
    fixtures = []
    support_data = support_gas = False

    def setUp(self):
        super(TestViewsWithoutData, self).setUp()

        for current_model in (ElectricityConsumption, GasConsumption, DayStatistics):
            current_model.objects.all().delete()

        self.assertFalse(ElectricityConsumption.objects.exists())
        self.assertFalse(GasConsumption.objects.exists())
        self.assertFalse(DayStatistics.objects.exists())


class TestViewsWithoutPrices(TestViews):
    """ Same tests as above, but without any price data as it's flushed in setUp().  """

    def setUp(self):
        super(TestViewsWithoutPrices, self).setUp()
        EnergySupplierPrice.objects.all().delete()
        self.assertFalse(EnergySupplierPrice.objects.exists())


class TestViewsWithoutGas(TestViews):
    """ Same tests as above, but without any GAS related data.  """
    fixtures = [
        'dsmr_frontend/test_dsmrreading_without_gas.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/test_energysupplierprice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
        'dsmr_frontend/test_electricity_consumption.json',
    ]
    support_gas = False

    def setUp(self):
        super(TestViewsWithoutGas, self).setUp()
        self.assertFalse(GasConsumption.objects.exists())
