from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_frontend.models.settings import FrontendSettings, SortedGraph


class TestSettings(TestCase):
    """ Tests for settings defaults. """

    def setUp(self):
        self.instance = FrontendSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(FrontendSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_merge_electricity_tariffs(self):
        self.assertFalse(self.instance.merge_electricity_tariffs)

    def test_electricity_delivered_color(self):
        self.assertEqual(self.instance.electricity_delivered_color, '#F05050')

    def test_electricity_delivered_alternate_color(self):
        self.assertEqual(self.instance.electricity_delivered_alternate_color, '#A43737')

    def test_electricity_returned_color(self):
        self.assertEqual(self.instance.electricity_returned_color, '#27C24C')

    def test_electricity_returned_alternate_color(self):
        self.assertEqual(self.instance.electricity_returned_alternate_color, '#166C2A')

    def test_gas_delivered_color(self):
        self.assertEqual(self.instance.gas_delivered_color, '#FF851B')

    def test_phase_delivered_l1_color(self):
        self.assertEqual(self.instance.phase_delivered_l1_color, '#A47448')

    def test_phase_delivered_l2_color(self):
        self.assertEqual(self.instance.phase_delivered_l2_color, '#A4484E')

    def test_phase_delivered_l3_color(self):
        self.assertEqual(self.instance.phase_delivered_l3_color, '#A44882')

    def test_temperature_color(self):
        self.assertEqual(self.instance.temperature_color, '#0073B7')

    def test_live_graphs_hours_range(self):
        self.assertEqual(self.instance.live_graphs_hours_range, 24)


class TestSortedGraph(TestCase):
    """ Tests for settings defaults. """

    def setUp(self):
        self.instance = SortedGraph()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(SortedGraph))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{}'.format(self.instance.__class__.__name__))
