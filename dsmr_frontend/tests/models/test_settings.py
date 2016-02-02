from django.test import TestCase

from dsmr_frontend.models.settings import FrontendSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = FrontendSettings().get_solo()

    def test_reverse_dashboard_graphs(self):
        self.assertFalse(self.instance.reverse_dashboard_graphs)
