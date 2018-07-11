from unittest import mock
import json

from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import DayStatistics
import dsmr_consumption.services


class TestViews(TestCase):
    """ Test whether views render at all. """
    fixtures = [
        'dsmr_frontend/test_dsmrreading.json',
        'dsmr_frontend/test_note.json',
        'dsmr_frontend/EnergySupplierPrice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
    ]
    namespace = 'frontend'
    support_data = True
    support_gas = True

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'unknown@localhost', 'passwd')
        dsmr_consumption.services.compact_all()

    def test_trends(self):
        response = self.client.get(
            reverse('{}:trends'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('capabilities', response.context)
        self.assertIn('frontend_settings', response.context)

    @mock.patch('django.utils.timezone.now')
    def test_trends_xhr_avg_consumption(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        response = self.client.get(
            reverse('{}:trends-xhr-avg-consumption'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
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
            reverse('{}:trends-xhr-avg-consumption'.format(self.namespace))
        )
        json_response = json.loads(response.content.decode("utf-8"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(json_response['electricity_returned']), 0)

    @mock.patch('django.utils.timezone.now')
    def test_trends_xhr_by_tariff(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        response = self.client.get(
            reverse('{}:trends-xhr-consumption-by-tariff'.format(self.namespace))
        )
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content.decode("utf-8"))

        if not self.support_data:
            return self.assertEqual(json_response, {})

        self.assertIn('week', json_response)
        self.assertIn('month', json_response)
        self.assertIn({'value': 84, 'name': 'electricity1'}, json_response['week'])
        self.assertIn({'value': 16, 'name': 'electricity2'}, json_response['week'])
        self.assertIn({'value': 84, 'name': 'electricity1'}, json_response['month'])
        self.assertIn({'value': 16, 'name': 'electricity2'}, json_response['month'])


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
        'dsmr_frontend/EnergySupplierPrice.json',
        'dsmr_frontend/test_statistics.json',
        'dsmr_frontend/test_meterstatistics.json',
    ]
    support_gas = False

    def setUp(self):
        super(TestViewsWithoutGas, self).setUp()
        self.assertFalse(GasConsumption.objects.exists())
