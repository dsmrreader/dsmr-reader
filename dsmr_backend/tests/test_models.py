from unittest import mock

from django.test import TestCase
from django.utils import timezone
import pytz

from dsmr_backend.models import ScheduledCall
from dsmr_backend.exceptions import DelayNextCall


class TestScheduledCall(TestCase):
    MODULE = 'dsmr_backend.tests.dummy.void_function'

    def setUp(self):
        ScheduledCall.objects.all().delete()
        self.instance = ScheduledCall.objects.create(name='Test', module_path=self.MODULE)

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'ScheduledCall')

    def test_managers(self):
        self.assertTrue(ScheduledCall.objects.callable().exists())
        ScheduledCall.objects.update(next_call=timezone.now() + timezone.timedelta(minutes=1))
        self.assertFalse(ScheduledCall.objects.callable().exists())

    def test_delay(self):
        self.assertTrue(ScheduledCall.objects.callable().exists())
        self.instance.delay(timezone.timedelta(minutes=1))
        self.assertFalse(ScheduledCall.objects.callable().exists())

    def test_execute_ok(self):
        self.assertEqual(self.instance.execute(), 'bla')

    @mock.patch(MODULE)
    def test_execute_return(self, bla_mock):
        bla_mock.return_value = 12345
        self.assertEqual(self.instance.execute(), 12345)

    @mock.patch(MODULE)
    def test_execute_exception(self, bla_mock):
        bla_mock.side_effect = LookupError()

        with self.assertRaises(LookupError):
            self.instance.execute()

    @mock.patch(MODULE)
    @mock.patch('django.utils.timezone.now')
    def test_execute_delay(self, now_mock, bla_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1), timezone=pytz.UTC)
        bla_mock.side_effect = DelayNextCall(hours=12)

        self.instance.execute()
        self.assertEqual(
            self.instance.next_call,
            timezone.datetime(2018, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        )


class TestDelayNextCall(TestCase):
    def test_delta(self):
        delta = timezone.timedelta(minutes=5)
        ex = DelayNextCall(minutes=5)
        self.assertEqual(ex.delta, delta)

    @mock.patch('django.utils.timezone.now')
    def test_timestamp(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2018, 1, 1), timezone=pytz.UTC)

        ex = DelayNextCall(timestamp=timezone.datetime(2018, 1, 1, 12, 5, 0, tzinfo=pytz.UTC))
        self.assertEqual(ex.delta, timezone.timedelta(hours=12, minutes=5))
