from django.test import TestCase, Client
from django.urls import reverse


class TestRegression(TestCase):
    """ Regression. """
    fixtures = ['dsmr_frontend/test_dsmrreading.json']

    def setUp(self):
        self.client = Client()

    def test_energysupplierprice_matching_query_does_not_exist(self):
        """ Test whether the dashboard no longer raises as DoesNotExist when prices are omitted. """
        self.client.get(reverse('frontend:dashboard'))
