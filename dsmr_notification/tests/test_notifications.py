from unittest import mock

from django.utils import timezone
from django.test import TestCase
from django.conf import settings
import pytz

from dsmr_backend.dto import Capability
from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_notification.models.settings import NotificationSetting, StatusNotificationSetting
from dsmr_stats.models.statistics import DayStatistics
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_notification.services
import dsmr_backend.services.backend


class TestServices(TestCase):
    """ Test dsmr_notification functions """
    fixtures = [
        'dsmr_notification/test_daystatistics.json',
        'dsmr_notification/test_electricity_consumption.json',
        'dsmr_notification/test_gas_consumption.json',
    ]
    API_KEY = 'qwertyuiopasdfghjklzxcvbnm'

    def setUp(self):
        NotificationSetting.get_solo()

    def test_notify_pre_check_default(self):
        """ Notifications: Test notify_pre_check() default behaviour. """
        notification_settings = NotificationSetting.get_solo()
        self.assertIsNone(notification_settings.notification_service)
        self.assertFalse(dsmr_notification.services.notify_pre_check())

    @mock.patch('dsmr_notification.services.notify_pre_check')
    def test_notify_pre_check_skip(self, notify_pre_check_mock):
        """ Notifications: Test whether notify_pre_check() skips current day. """
        notify_pre_check_mock.return_value = False

        notification_settings = NotificationSetting.get_solo()
        self.assertIsNone(notification_settings.notification_service)
        self.assertFalse(dsmr_notification.services.notify())

    @mock.patch('dsmr_notification.services.send_notification')
    @mock.patch('django.utils.timezone.now')
    def test_notify_pre_check_dummy_message(self, now_mock, send_notification_mock):
        """ Notifications: Test notify_pre_check()'s output when service is set """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1, 0, 0, 0))

        # Should fail because we haven't set a service
        self.assertFalse(dsmr_notification.services.notify_pre_check())

        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.save()

        # Should be okay now, with dummy message being sent.
        self.assertFalse(send_notification_mock.called)
        self.assertIsNone(NotificationSetting.get_solo().next_notification)
        self.assertTrue(dsmr_notification.services.notify_pre_check())  # Execution
        self.assertTrue(send_notification_mock.called)
        self.assertIsNotNone(NotificationSetting.get_solo().next_notification)

        # 'next_notification' is no longer empty, so we should run the normal flow now.
        # First we verify the next_notification check.
        now_mock.return_value = now_mock.return_value - timezone.timedelta(minutes=1)
        self.assertFalse(dsmr_notification.services.notify_pre_check())

        # And finally, the flow we were used to.
        now_mock.return_value = now_mock.return_value + timezone.timedelta(minutes=5)
        self.assertTrue(dsmr_notification.services.notify_pre_check())

    @mock.patch('django.utils.timezone.now')
    def test_set_next_notification_date(self, now_mock):
        """ Notifications: Test if next notification date is set """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 16, 0, 0, 0))

        now = timezone.localtime(timezone.now())
        NotificationSetting.objects.update(next_notification=now)

        dsmr_notification.services.set_next_notification()

        notification_settings = NotificationSetting.get_solo()
        self.assertEqual(
            notification_settings.next_notification,
            timezone.make_aware(timezone.datetime(2016, 11, 17, 6, 0, 0))
        )

    @mock.patch('django.utils.timezone.now')
    def test_set_next_notification_date_for_dst_change(self, now_mock):
        """ Notifications: Test if next notification date is set due to DST change """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 10, 27, 2, 0, 0))  # Do NOT change hour.
        now = timezone.localtime(timezone.now())
        NotificationSetting.objects.update(next_notification=now)

        # This used to trigger a AmbiguousTimeError.
        dsmr_notification.services.set_next_notification()

        notification_settings = NotificationSetting.get_solo()
        next_notification = timezone.localtime(notification_settings.next_notification)
        expected = timezone.datetime(2018, 10, 28, 6, 0, 0)
        expected = timezone.localtime(timezone.make_aware(expected, pytz.timezone(settings.TIME_ZONE), is_dst=True))

        self.assertEqual(next_notification, expected)

        # Check other way around as well, in March.
        now_mock.return_value = timezone.make_aware(timezone.datetime(2019, 3, 30, 1, 0, 0))  # Do NOT change hour.
        now = timezone.localtime(timezone.now())
        NotificationSetting.objects.update(next_notification=now)

        dsmr_notification.services.set_next_notification()

        notification_settings = NotificationSetting.get_solo()
        next_notification = timezone.localtime(notification_settings.next_notification)
        expected = timezone.datetime(2019, 3, 31, 6, 0, 0)
        expected = timezone.localtime(timezone.make_aware(expected, pytz.timezone(settings.TIME_ZONE), is_dst=True))
        self.assertEqual(next_notification, expected)

    @mock.patch('dsmr_notification.services.send_notification')
    def test_no_daystatistics(self, send_notification_mock):
        """ Notifications: Test no notification sent because of no stats """
        DayStatistics.objects.all().delete()

        NotificationSetting.objects.update(
            notification_service=NotificationSetting.NOTIFICATION_PROWL,
            prowl_api_key=self.API_KEY,
            next_notification=timezone.now(),
        )

        self.assertFalse(send_notification_mock.called)
        dsmr_notification.services.notify()
        self.assertFalse(send_notification_mock.called)

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_notification_api_fail_4xx(self, now_mock, requests_post_mock):
        """ Notifications: Test API failure for notify() - HTTP 4xx """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 17, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(status_code=403, text='Forbidden')

        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.prowl_api_key = self.API_KEY
        notification_settings.next_notification = timezone.now()
        notification_settings.save()

        # When having no data, this should NOT raise an exception.
        if not self.fixtures:
            return dsmr_notification.services.notify()

        with self.assertRaises(AssertionError):
            dsmr_notification.services.notify()

        # HTTP 4xx should RESET all settings.
        notification_settings = NotificationSetting.get_solo()
        self.assertIsNone(notification_settings.notification_service)
        self.assertIsNone(notification_settings.pushover_api_key)
        self.assertIsNone(notification_settings.pushover_user_key)
        self.assertIsNone(notification_settings.prowl_api_key)
        self.assertIsNone(notification_settings.next_notification)

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_notification_api_fail_5xx(self, now_mock, requests_post_mock):
        """ Notifications: Test API failure for notify() - HTTP 5xx """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 17, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(status_code=503, text='Server Error')

        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.prowl_api_key = self.API_KEY
        notification_settings.next_notification = timezone.now()
        notification_settings.save()

        # When having no data, this should NOT raise an exception.
        if not self.fixtures:
            return dsmr_notification.services.notify()

        with self.assertRaises(AssertionError):
            dsmr_notification.services.notify()

        # HTTP 5xx should delay next call.
        notification_settings = NotificationSetting.get_solo()
        self.assertIsNotNone(notification_settings.notification_service)
        self.assertIsNotNone(notification_settings.prowl_api_key)
        self.assertGreater(notification_settings.next_notification, timezone.now())

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_notification_api_fail_other(self, now_mock, requests_post_mock):
        """ Notifications: Test API failure for notify() - HTTP xxx """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 17, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(status_code=300, text='xxxxx')  # Just for code coverage.

        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.prowl_api_key = self.API_KEY
        notification_settings.next_notification = timezone.now()
        notification_settings.save()

        # When having no data, this should NOT raise an exception.
        if not self.fixtures:
            return dsmr_notification.services.notify()

        with self.assertRaises(AssertionError):
            dsmr_notification.services.notify()

    @mock.patch('dsmr_notification.signals.notification_sent.send_robust')
    @mock.patch('django.utils.timezone.now')
    def test_notification_dummy_provider_signal(self, now_mock, send_robust_mock):
        if not self.fixtures:
            return

        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 17, hour=0, minute=5))

        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_DUMMY
        notification_settings.next_notification = timezone.now()
        notification_settings.save()

        self.assertFalse(send_robust_mock.called)
        dsmr_notification.services.notify()
        self.assertTrue(send_robust_mock.called)

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_notifications(self, now_mock, requests_post_mock):
        """ Notifications: Test notify() (actual notification sender)"""
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 11, 18, hour=0, minute=5))
        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='OK')

        notification_settings = NotificationSetting.get_solo()
        self.assertIsNone(notification_settings.next_notification)
        self.assertFalse(requests_post_mock.called)

        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.prowl_api_key = self.API_KEY
        notification_settings.next_notification = timezone.now()
        notification_settings.save()

        dsmr_notification.services.notify()

        if self.fixtures:
            self.assertTrue(requests_post_mock.called)
        else:
            return self.assertFalse(requests_post_mock.called)

        # Next notification should be pushed.
        self.assertGreater(NotificationSetting.get_solo().next_notification, timezone.now())

    @mock.patch('requests.post')
    @mock.patch('django.utils.timezone.now')
    def test_check_status(self, now_mock, requests_post_mock):
        """ Check whether downtime of the datalogger triggers notifications. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1, hour=12))
        requests_post_mock.return_value = mock.MagicMock(status_code=200, text='OK')

        StatusNotificationSetting.get_solo()
        notification_settings = NotificationSetting.get_solo()
        notification_settings.notification_service = NotificationSetting.NOTIFICATION_PROWL
        notification_settings.prowl_api_key = self.API_KEY
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
            timestamp=timezone.now() - timezone.timedelta(minutes=15),
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

        self.assertFalse(requests_post_mock.called)
        dsmr_notification.services.check_status()
        self.assertTrue(requests_post_mock.called)


class TestServicesWithoutGas(TestServices):
    """ Same tests, but without having any gas data. """
    fixtures = [
        'dsmr_notification/test_daystatistics.json',
    ]

    def setUp(self):
        super(TestServicesWithoutGas, self).setUp()
        DayStatistics.objects.all().update(gas=None)
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.GAS))


class TestServicesWithoutElectricityReturned(TestServices):
    """ Same tests, but without having any electricity returned. """

    def setUp(self):
        super(TestServicesWithoutElectricityReturned, self).setUp()
        DayStatistics.objects.all().update(electricity1_returned=0, electricity2_returned=0)
        ElectricityConsumption.objects.update(currently_returned=0)
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.ELECTRICITY_RETURNED))


class TestServicesWithPrices(TestServices):
    """ Same tests, with prices set. """

    def setUp(self):
        super(TestServicesWithPrices, self).setUp()
        EnergySupplierPrice.objects.create(
            start=DayStatistics.objects.all()[0].day,
            end=DayStatistics.objects.all()[0].day,
            description='Test',
            electricity_delivered_1_price=3,
            electricity_delivered_2_price=5,
            electricity_returned_1_price=1,
            electricity_returned_2_price=2,
            gas_price=8,
            fixed_daily_cost=7,
        )
        self.assertTrue(dsmr_backend.services.backend.get_capability(Capability.COSTS))


class TestServicesWithoutPrices(TestServices):
    """ Same tests, but WITHOUT any prices set. """

    def setUp(self):
        super(TestServicesWithoutPrices, self).setUp()
        EnergySupplierPrice.objects.all().delete()
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.COSTS))


class TestServicesWithoutAnyData(TestServices):
    """ Same tests, but without having any data at all. """
    fixtures = []

    def setUp(self):
        super(TestServicesWithoutAnyData, self).setUp()
        self.assertFalse(dsmr_backend.services.backend.get_capability(Capability.ANY))
