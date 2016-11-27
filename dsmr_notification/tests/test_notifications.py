from unittest import mock

from django.test import TestCase
from django.utils import timezone
from django.utils.translation import ugettext_lazy

from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_notification.models.settings import NotificationSetting
from dsmr_stats.models.statistics import DayStatistics
import dsmr_notification.services
import dsmr_backend


class TestServices(TestCase):
    """ Test dsmr_notification functions """
    fixtures = [
        'dsmr_notification/test_daystatistics.json',
        'dsmr_notification/test_electricity_consumption.json',
        'dsmr_notification/test_gas_consumption.json',
    ]

    def test_hardcoded_properties(self):
        """ Notifications: Test service-delivered hardcoded values """

        sender_priority = dsmr_notification.services.get_notification_priority()
        sender_name = dsmr_notification.services.get_notification_sender_name()
        sender_event = dsmr_notification.services.get_notification_event_name()

        self.assertEqual('-2', sender_priority)
        self.assertEqual('DSMR-Reader', sender_name)
        self.assertEquals(type(str('dsmr')), type(sender_event))
        self.assertEqual(ugettext_lazy('Daily usage notification'),
                         sender_event)

    def test_should_notify_default(self):
        """ Notifications: Test should_notify() default behaviour. """

        settings = NotificationSetting.get_solo()
        self.assertFalse(settings.send_notification)
        self.assertFalse(dsmr_notification.services.should_notify(settings))

    def test_should_notify_skip(self):
        """ Notifications: Test whether should_notify() skips current day. """

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

        settings.next_notification = None
        dsmr_notification.services.set_next_notification(
            settings, timezone.make_aware(timezone.datetime(2116, 11, 16)))
        self.assertFalse(dsmr_notification.services.should_notify(settings))

    @mock.patch('django.utils.timezone.now')
    def test_set_next_notification_date(self, now_mock):
        """ Notifications: Test if next notification date is set """
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 11, 16))

        now = timezone.localtime(timezone.now())
        tomorrow = (timezone.localtime(timezone.now()) +
                    timezone.timedelta(hours=24)).date()

        settings = NotificationSetting.get_solo()
        settings.next_notification = now
        settings.save()

        dsmr_notification.services.set_next_notification(settings, now)

        self.assertEqual(settings.next_notification, tomorrow)

    def test_invalid_api_url(self):
        """ Notifications: Test if inappropriate services get caught """

        settings = NotificationSetting.get_solo()
        settings.send_notification = True
        settings.notification_service = 'DSMR-Reader-Rulez'
        settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        settings.save()

        with self.assertRaises(AssertionError):
            dsmr_notification.services.notify()

    def test_no_daystatistics(self):
        """ Notifications: Test no notification because of no stats"""

        DayStatistics.objects.all().delete()

        settings = NotificationSetting.get_solo()
        settings.send_notification = True
        settings.notification_service = NotificationSetting.NOTIFICATION_NMA
        settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        settings.save()

        self.assertFalse(dsmr_notification.services.notify())

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_notification_api_fail(self, now_mock, requests_post_mock):
        """ Notifications: Test API failure for notify() """
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 11, 17, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(
            status_code=403, text='Forbidden')

        settings = NotificationSetting.get_solo()
        settings.send_notification = True
        settings.notification_service = NotificationSetting.NOTIFICATION_NMA
        settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        settings.next_notification = timezone.localtime(timezone.now())
        settings.save()

        if self.fixtures:
            with self.assertRaises(AssertionError):
                dsmr_notification.services.notify()
        else:
            # When having no data, this should NOT raise an exception.
            return dsmr_notification.services.notify()

        with self.assertRaisesMessage(
                AssertionError, 'Notify API call failed: Forbidden (HTTP403)'):
            dsmr_notification.services.notify()

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_notifications(self, now_mock, requests_post_mock):
        """ Notifications: Test notify() (actual notification sender)"""
        now_mock.return_value = timezone.make_aware(
            timezone.datetime(2016, 11, 17, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(
            status_code=200, text='OK')

        settings = NotificationSetting.get_solo()
        self.assertFalse(settings.send_notification)
        self.assertIsNone(settings.next_notification)
        self.assertFalse(requests_post_mock.called)

        settings.send_notification = True
        settings.notification_service = NotificationSetting.NOTIFICATION_NMA
        settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        settings.next_notification = timezone.localtime(timezone.now())
        settings.save()

        dsmr_notification.services.notify()

        settings = NotificationSetting.get_solo()

        if self.fixtures:
            self.assertTrue(requests_post_mock.called)
        else:
            return self.assertFalse(requests_post_mock.called)

        nma_url = dsmr_notification.services.get_notification_api_url(settings)
        yesterday = (timezone.localtime(timezone.now()) -
                     timezone.timedelta(hours=24)).date()
        stats = DayStatistics.objects.get(day=yesterday)
        api_msg = dsmr_notification.services.create_notification_message(yesterday, stats)
        self.assertTrue(yesterday.strftime("%d-%m-%Y") in api_msg)

        # Dissect call
        requests_post_mock.assert_called_once_with(nma_url, {
            'apikey': settings.api_key,
            'priority': dsmr_notification.services.get_notification_priority(),
            'application': dsmr_notification.services.get_notification_sender_name(),
            'event': dsmr_notification.services.get_notification_event_name(),
            'description': api_msg
        })

        tomorrow = (timezone.localtime(timezone.now()) +
                    timezone.timedelta(hours=24)).date()
        self.assertEqual(settings.next_notification, tomorrow)


class TestServicesWithoutGas(TestServices):
    """ Same tests, but without having any gas data. """
    fixtures = [
        'dsmr_notification/test_daystatistics.json',
    ]

    def setUp(self):
        super(TestServicesWithoutGas, self).setUp()
        DayStatistics.objects.all().update(gas=None)
        self.assertFalse(dsmr_backend.services.get_capabilities(capability='gas'))


class TestServicesWithoutElectricityReturned(TestServices):
    """ Same tests, but without having any electricity returned. """
    def setUp(self):
        super(TestServicesWithoutElectricityReturned, self).setUp()
        DayStatistics.objects.all().update(electricity1_returned=0, electricity2_returned=0)
        ElectricityConsumption.objects.update(currently_returned=0)
        self.assertFalse(dsmr_backend.services.get_capabilities(capability='electricity_returned'))


class TestServicesWithoutAnyData(TestServices):
    """ TSame tests, but without having any data at all. """
    fixtures = []

    def setUp(self):
        super(TestServicesWithoutAnyData, self).setUp()
        self.assertFalse(dsmr_backend.services.get_capabilities(capability='any'))
