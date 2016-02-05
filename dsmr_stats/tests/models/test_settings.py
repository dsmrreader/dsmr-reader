from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_stats.models.settings import StatsSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = StatsSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(StatsSettings))

    def test_track(self):
        self.assertTrue(self.instance.track)
