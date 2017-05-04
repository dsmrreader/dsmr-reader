from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_api.models import APISettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = APISettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(APISettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_allow(self):
        self.assertFalse(self.instance.allow)

    def test_auth_key(self):
        self.assertIsNotNone(self.instance.auth_key)
