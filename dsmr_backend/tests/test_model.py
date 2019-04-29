from unittest import mock

from django.test import TestCase
from django.utils import timezone
from django.contrib.admin.sites import site

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.models.settings import EmailSettings


class TestScheduledProcess(TestCase):
    MODULE = 'dsmr_backend.tests.dummy.void_function'

    def setUp(self):
        ScheduledProcess.objects.all().delete()
        self.instance = ScheduledProcess.objects.create(name='Test', module=self.MODULE)

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'ScheduledProcess')

    def test_managers(self):
        self.assertTrue(ScheduledProcess.objects.ready().exists())
        ScheduledProcess.objects.update(planned=timezone.now() + timezone.timedelta(minutes=1))
        self.assertFalse(ScheduledProcess.objects.ready().exists())

    def test_delay(self):
        self.assertTrue(ScheduledProcess.objects.ready().exists())
        self.instance.delay(timezone.timedelta(minutes=1))
        self.assertFalse(ScheduledProcess.objects.ready().exists())

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


class EmailSettingsSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = EmailSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(EmailSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))
