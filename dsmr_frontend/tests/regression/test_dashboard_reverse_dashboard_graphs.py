import json

from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_frontend.models.settings import FrontendSettings


class TestRegression(TestCase):
    """ Regression. """
    fixtures = ['dsmr_frontend/test_reverse_dashboard_graphs.json']

    def setUp(self):
        self.client = Client()

    def test_energysupplierprice_matching_query_does_not_exist(self):
        """ Test whether default sorting slices consumption as intended. """
        self.assertFalse(FrontendSettings().get_solo().reverse_dashboard_graphs)
        self.assertEqual(ElectricityConsumption.objects.count(), 1)
        self.assertEqual(GasConsumption.objects.count(), 100)

        response = self.client.get(
            reverse('frontend:dashboard')
        )
        self.assertIn('gas_x', response.context)

        # This will fail when the fix has been reverted.
        self.assertEqual(json.loads(response.context['gas_x'])[0], 'Tue 2 a.m.')
