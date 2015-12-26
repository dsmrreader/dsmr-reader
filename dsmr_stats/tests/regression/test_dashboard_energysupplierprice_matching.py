from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.management import call_command


class TestRegression(TestCase):
    """ Regression. """
    fixtures = ['test_dsmrreading.json']

    def setUp(self):
        self.client = Client()

    def test_energysupplierprice_matching_query_does_not_exist(self):
        call_command('dsmr_stats_compactor')
        # This used to raise EnergySupplierPrice.DoesNotExist when no price fixtures are loaded.
        self.client.get(
            reverse('stats:dashboard')
        )
