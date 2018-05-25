from unittest import mock

from django.test import TestCase
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_notification.models.settings import NotificationSetting, StatusNotificationSetting
from dsmr_stats.models.statistics import DayStatistics
import dsmr_notification.services
import dsmr_backend
from dsmr_datalogger.models.reading import DsmrReading


class TestServices(TestCase):
    """ Test dsmr_notification functions """
    fixtures = [
        'dsmr_notification/test_daystatistics.json',
        'dsmr_notification/test_electricity_consumption.json',
        'dsmr_notification/test_gas_consumption.json',
    ]

    def test_should_notify_default(self):
        """ Notifications: Test should_notify() default behaviour. """

        notification_settings = NotificationSetting.get_solo()
        self.assertIsNone(notification_settings.notification_service)
        self.assertFalse(dsmr_notification.services.should_notify())

    @mock.patch('dsmr_notification.services.should_notify')
    def test_should_notify_skip(self, should_notify_mock):
        """ Notifications: Test whether should_notify() skips current day. """
        should_notify_mock.return_value = False

        notification_settings = NotificationSetting.get_solo()
        self.assertIsNone(notification_settings.notification_service)
        self.assertFalse(dsmr_notification.services.notify())

    def test_should_notify_set(self):
        """ Notifications: Test should_notify()'s output when service is set """

        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.save()

        # Should fail because we haven't set an API key
        self.assertFalse(dsmr_notification.services.should_notify())

        notification_settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        notification_settings.save()
        self.assertTrue(dsmr_notification.services.should_notify())

        notification_settings.next_notification = None
        dsmr_notification.services.set_next_notification(timezone.make_aware(timezone.datetime(2116, 11, 16)))
        self.assertFalse(dsmr_notification.services.should_notify())

    @mock.patch('django.utils.timezone.now')
    def test_set_next_notification_date(self, now_mock):
        """ Notifications: Test if next notification date is set """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 16))

        now = (timezone.localtime(timezone.now()))
        tomorrow = (timezone.localtime(timezone.now()) + timezone.timedelta(hours=24)).date()
        notification_settings = NotificationSetting.get_solo()
        notification_settings.next_notification = now.date()
        notification_settings.save()

        dsmr_notification.services.set_next_notification(now)

        notification_settings = NotificationSetting.get_solo()
        self.assertEqual(notification_settings.next_notification, tomorrow)

    def test_no_daystatistics(self):
        """ Notifications: Test no notification because of no stats"""

        DayStatistics.objects.all().delete()

        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        notification_settings.save()

        self.assertFalse(dsmr_notification.services.notify())

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_notification_api_fail(self, now_mock, requests_post_mock):
        """ Notifications: Test API failure for notify() """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 17, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(status_code=403, text='Forbidden')

        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        notification_settings.next_notification = timezone.localtime(timezone.now())
        notification_settings.save()

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
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 17, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='OK')

        notification_settings = NotificationSetting.get_solo()
        self.assertIsNone(notification_settings.next_notification)
        self.assertFalse(requests_post_mock.called)

        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.api_key = 'es7sh2d-DSMR-Reader-Rulez-iweu732'
        notification_settings.next_notification = timezone.localtime(timezone.now())
        notification_settings.save()

        dsmr_notification.services.notify()

        notification_settings = NotificationSetting.get_solo()

        if self.fixtures:
            self.assertTrue(requests_post_mock.called)
        else:
            return self.assertFalse(requests_post_mock.called)

        nma_url = NotificationSetting.NOTIFICATION_API_URL[notification_settings.notification_service]
        yesterday = (timezone.localtime(timezone.now()) - timezone.timedelta(hours=24)).date()
        stats = DayStatistics.objects.get(day=yesterday)
        api_msg = dsmr_notification.services.create_consumption_notification_message(yesterday, stats)
        self.assertTrue(yesterday.strftime("%d-%m-%Y") in api_msg)

        # Dissect call
        requests_post_mock.assert_called_once_with(nma_url, {
            'apikey': notification_settings.api_key,
            'priority': '-2',
            'application': 'DSMR-Reader',
            'event': 'Daily usage notification',
            'description': api_msg
        })

        tomorrow = (timezone.localtime(timezone.now()) + timezone.timedelta(hours=24)).date()
        self.assertEqual(notification_settings.next_notification, tomorrow)

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_check_status(self, now_mock, requests_post_mock):
        """ Check whether downtime of the datalogger triggers notifications. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1, hour=12))
        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='OK')

        StatusNotificationSetting.get_solo()
        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.api_key = 'test'
        notification_settings.save()

        # Schedule ahead.
        StatusNotificationSetting.objects.update(next_check=timezone.now() + timezone.timedelta(minutes=1))
        dsmr_notification.services.check_status()

        # No data.
        StatusNotificationSetting.objects.update(next_check=timezone.now())
        DsmrReading.objects.all().delete()
        dsmr_notification.services.check_status()
        self.assertGreater(StatusNotificationSetting.get_solo().next_check, timezone.now())

        # Recent data.
        StatusNotificationSetting.objects.update(next_check=timezone.now())
        DsmrReading.objects.create(
            timestamp=timezone.now() - timezone.timedelta(minutes=45),
            electricity_delivered_1=1,
            electricity_returned_1=2,
            electricity_delivered_2=3,
            electricity_returned_2=4,
            electricity_currently_delivered=5,
            electricity_currently_returned=6,
        )
        dsmr_notification.services.check_status()

        self.assertGreater(StatusNotificationSetting.get_solo().next_check, timezone.now())
        self.assertFalse(requests_post_mock.called)

        # Data from a while ago.
        StatusNotificationSetting.objects.update(next_check=timezone.now())
        DsmrReading.objects.all().delete()
        DsmrReading.objects.create(
            timestamp=timezone.now() - timezone.timedelta(hours=24),
            electricity_delivered_1=1,
            electricity_returned_1=2,
            electricity_delivered_2=3,
            electricity_returned_2=4,
            electricity_currently_delivered=5,
            electricity_currently_returned=6,
        )

        StatusNotificationSetting.objects.update(next_check=timezone.now())
        nma_url = NotificationSetting.NOTIFICATION_API_URL[notification_settings.notification_service]

        self.assertFalse(requests_post_mock.called)
        dsmr_notification.services.check_status()
        self.assertTrue(requests_post_mock.called)

        # Dissect call
        requests_post_mock.assert_called_once_with(nma_url, {
            'apikey': 'test',
            'priority': '-2',
            'application': 'DSMR-Reader',
            'event': 'Datalogger check',
            'description': 'It has been over an hour since the last reading received. Please check your datalogger.'
        })


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
