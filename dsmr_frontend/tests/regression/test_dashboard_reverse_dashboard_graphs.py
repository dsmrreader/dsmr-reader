from unittest import mock
import json

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption


class TestRegression(TestCase):
    """ Regression. """
    fixtures = ['dsmr_frontend/test_reverse_dashboard_graphs.json']

    def setUp(self):
        self.client = Client()

    @mock.patch('django.utils.timezone.now')
    def test_dashboard_reverse_dashboard_graphs(self, now_mock):
        """ Test whether default sorting slices consumption as intended. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2015, 12, 16))

        self.assertEqual(ElectricityConsumption.objects.count(), 1)
        self.assertEqual(GasConsumption.objects.count(), 100)

        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('frontend:dashboard-xhr-graphs'))
        self.assertEqual(response.status_code, 200)
        json_content = json.loads(response.content.decode("utf8"))

        # This will fail when the fix has been reverted.
        self.assertIn('gas_x', json_content)
        self.assertEqual(json_content['gas_x'][0], '8 p.m.')
