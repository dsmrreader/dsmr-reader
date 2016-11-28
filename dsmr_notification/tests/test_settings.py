from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_notification.models.settings import NotificationSetting


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = NotificationSetting().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(NotificationSetting))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_reverse_send_notification(self):
        self.assertFalse(self.instance.send_notification)

    def test_notification_service(self):
        self.assertEqual(self.instance.notification_service, NotificationSetting.NOTIFICATION_NMA)

    def test_api_key(self):
        self.assertIsNone(self.instance.api_key)

    def test_next_notification(self):
        self.assertIsNone(self.instance.next_notification)
