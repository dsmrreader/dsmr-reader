from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_frontend.models.settings import FrontendSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = FrontendSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(FrontendSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_reverse_dashboard_graphs(self):
        self.assertFalse(self.instance.reverse_dashboard_graphs)

    def test_merge_electricity_tariffs(self):
        self.assertFalse(self.instance.merge_electricity_tariffs)

    def test_electricity_delivered_color(self):
        self.assertEqual(self.instance.electricity_delivered_color, '#F05050')

    def test_electricity_delivered_alternate_color(self):
        self.assertEqual(self.instance.electricity_delivered_alternate_color, '#7D311A')

    def test_electricity_returned_color(self):
        self.assertEqual(self.instance.electricity_returned_color, '#27C24C')

    def test_electricity_returned_alternate_color(self):
        self.assertEqual(self.instance.electricity_returned_alternate_color, '#C8C864')

    def test_gas_delivered_color(self):
        self.assertEqual(self.instance.gas_delivered_color, '#FF851B')

    def test_temperature_color(self):
        self.assertEqual(self.instance.temperature_color, '#0073B7')
