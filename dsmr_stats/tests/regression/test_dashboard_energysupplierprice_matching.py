from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from django.core.management import call_command


class TestRegression(TestCase):
    """ Regression. """
    fixtures = ['dsmr_stats/test_dsmrreading.json']

    def setUp(self):
        self.client = Client()

    def test_energysupplierprice_matching_query_does_not_exist(self):
        """ Test whether the dashboard no longer raises as DoesNotExist when prices are omitted. """
        call_command('dsmr_stats_compactor')

        self.client.get(
            reverse('stats:dashboard')
        )
