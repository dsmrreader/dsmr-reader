from datetime import time

from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_backup.models.settings import BackupSettings, DropboxSettings


class TestBackupSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = BackupSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(BackupSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_daily_backup(self):
        self.assertTrue(self.instance.daily_backup)

    def test_compress(self):
        self.assertTrue(self.instance.compress)

    def test_backup_time(self):
        self.assertTrue(self.instance.backup_time, time(hour=2))

    def test_latest_backup(self):
        self.assertIsNone(self.instance.latest_backup)


class TestDropboxSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = DropboxSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(DropboxSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_access_token(self):
        self.assertIsNone(self.instance.access_token)

    def test_latest_sync(self):
        self.assertIsNone(self.instance.latest_sync)
