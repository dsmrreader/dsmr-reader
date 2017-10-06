from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_pvoutput.models.settings import PVOutputAPISettings, PVOutputAddStatusSettings


class TestPVOutputAPISettings(TestCase):
    def setUp(self):
        self.instance = PVOutputAPISettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(PVOutputAPISettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_auth_token(self):
        self.assertIsNone(self.instance.auth_token)

    def test_system_identifier(self):
        self.assertIsNone(self.instance.system_identifier)


class TestPVOutputAddStatusSettings(TestCase):
    def setUp(self):
        self.instance = PVOutputAddStatusSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(PVOutputAddStatusSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_export(self):
        self.assertFalse(self.instance.export)

    def test_upload_interval(self):
        self.assertEqual(self.instance.upload_interval, PVOutputAddStatusSettings.INTERVAL_5_MINUTES)

    def test_upload_delay(self):
        self.assertEqual(self.instance.upload_delay, 0)

    def test_processing_delay(self):
        self.assertIsNone(self.instance.processing_delay)

    def test_next_export(self):
        self.assertIsNone(self.instance.next_export)
