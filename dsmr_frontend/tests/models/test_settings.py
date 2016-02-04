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

    def test_reverse_dashboard_graphs(self):
        self.assertFalse(self.instance.reverse_dashboard_graphs)

    def test_recent_history_weeks(self):
        self.assertEqual(self.instance.recent_history_weeks, 4)
