from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_notification.models.settings import NotificationSetting, StatusNotificationSetting


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = NotificationSetting().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(NotificationSetting))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_notification_service(self):
        self.assertIsNone(self.instance.notification_service)

    def test_pushover_api_key(self):
        self.assertIsNone(self.instance.pushover_api_key)

    def test_pushover_user_key(self):
        self.assertIsNone(self.instance.pushover_user_key)

    def test_prowl_api_key(self):
        self.assertIsNone(self.instance.prowl_api_key)

    def test_next_notification(self):
        self.assertIsNone(self.instance.next_notification)


class TestStatusNotificationSetting(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = StatusNotificationSetting().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(StatusNotificationSetting))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_next_check(self):
        self.assertIsNone(self.instance.next_check)
