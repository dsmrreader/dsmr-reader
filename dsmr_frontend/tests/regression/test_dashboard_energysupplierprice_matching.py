from django.test import TestCase, Client
from django.core.urlresolvers import reverse

from dsmr_backend.tests.mixins import CallCommandStdoutMixin


class TestRegression(CallCommandStdoutMixin, TestCase):
    """ Regression. """
    fixtures = ['dsmr_frontend/test_dsmrreading.json']

    def setUp(self):
        self.client = Client()

    def test_energysupplierprice_matching_query_does_not_exist(self):
        """ Test whether the dashboard no longer raises as DoesNotExist when prices are omitted. """
#        self._call_command_stdout('dsmr_backend')

        self.client.get(
            reverse('frontend:dashboard')
        )
