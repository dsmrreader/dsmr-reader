from django.test import TestCase

from dsmr_stats.models.settings import StatsSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = StatsSettings().get_solo()

    def test_reverse_dashboard_graphs(self):
        self.assertFalse(self.instance.reverse_dashboard_graphs)
