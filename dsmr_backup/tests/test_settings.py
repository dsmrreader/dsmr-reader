from datetime import time

from django.conf import settings
from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backup.models.settings import BackupSettings, DropboxSettings, EmailBackupSettings


class TestBackupSettings(TestCase):
    def setUp(self):
        self.instance = BackupSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(BackupSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_daily_backup(self):
        self.assertTrue(self.instance.daily_backup)

    def test_backup_time(self):
        self.assertTrue(self.instance.backup_time, time(hour=2))


class TestDropboxSettings(TestCase):
    def setUp(self):
        self.instance = DropboxSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(DropboxSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_refresh_token(self):
        self.assertIsNone(self.instance.refresh_token)


class TestEmailBackupSettings(TestCase):
    def setUp(self):
        self.instance = EmailBackupSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(EmailBackupSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_interval(self):
        self.assertIsNone(self.instance.interval)

    def test_handle_settings_update_hook(self):
        sp = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_EMAIL_BACKUP)
        self.assertFalse(sp.active)

        self.instance.interval = EmailBackupSettings.INTERVAL_DAILY
        self.instance.save()

        sp.refresh_from_db()
        self.assertTrue(sp.active)
