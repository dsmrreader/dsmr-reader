from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_stats.models.note import Note


class TestNote(TestCase):
    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(Note))
