from unittest import mock
import json

from django.test import TestCase
from django.utils import timezone

from dsmr_notification.models.settings import NotificationSetting
import dsmr_notification.services


class TestServices(TestCase):
    """ Test dsmr_notification functions """
    fixtures = ['dsmr_notification/test_daystatistics.json']

    def test_should_notify_default(self):
        """ Notifications: Test should_notify() default behaviour. """

        settings = NotificationSetting.get_solo()
        self.assertFalse(settings.send_notification)
        self.assertFalse(dsmr_notification.services.should_notify(settings))

    def test_should_notify_set(self):
        """ Notifications: Test should_notify()'s output when service is set """

        settings = NotificationSetting.get_solo()
        settings.send_notification = True
        settings.notification_service = NotificationSetting.NOTIFICATION_NMA
        settings.save()
        self.assertTrue(settings.send_notification)

        # Should fail because we haven't set an API key
        self.assertFalse(dsmr_notification.services.should_notify(settings))

        settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        settings.save()
        self.assertTrue(dsmr_notification.services.should_notify(settings))

    @mock.patch('django.utils.timezone.now')
    def test_set_next_notification_date(self, now_mock):
        """ Notifications: Test if next notification date is set """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 16))

        now = timezone.localtime(timezone.now())
        tomorrow = (timezone.localtime(timezone.now()) +
                    timezone.timedelta(hours=24)).date()

        settings = NotificationSetting.get_solo()
        settings.next_notification = now
        settings.save()

        dsmr_notification.services.set_next_notification(settings, now)

        self.assertEqual(settings.next_notification, tomorrow)
