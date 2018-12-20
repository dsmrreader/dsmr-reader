from unittest import mock
import tempfile
import shutil
import gzip
import os

from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_backup.models.settings import BackupSettings
import dsmr_backup.services.backup


class TestBackupServices(InterceptStdoutMixin, TestCase):
    @mock.patch('dsmr_backup.services.backup.create')
    def test_check_backups_disabled(self, create_backup_mock):
        backup_settings = BackupSettings.get_solo()
        backup_settings.daily_backup = False
        backup_settings.save()

        self.assertFalse(BackupSettings.get_solo().daily_backup)
        self.assertFalse(create_backup_mock.called)

        # Should create initial backup.
        dsmr_backup.services.backup.check()
        self.assertFalse(create_backup_mock.called)

    @mock.patch('dsmr_backup.services.backup.create')
    @mock.patch('django.utils.timezone.now')
    def test_check_initial(self, now_mock, create_backup_mock):
        """ Test whether a initial backup is created immediately. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1, hour=18))
        self.assertFalse(create_backup_mock.called)

        # Should create initial backup.
        dsmr_backup.services.backup.check()
        self.assertTrue(create_backup_mock.called)

    @mock.patch('dsmr_backup.services.backup.create')
    @mock.patch('django.utils.timezone.now')
    def test_check_interval_restriction(self, now_mock, create_backup_mock):
        """ Test whether backups are restricted by one backup per day. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1, hour=1, minute=5))

        # Fake latest backup.
        now = timezone.localtime(timezone.now())
        backup_settings = BackupSettings.get_solo()
        backup_settings.latest_backup = now
        backup_settings.backup_time = (now - timezone.timedelta(minutes=1)).time()
        backup_settings.save()

        self.assertIsNotNone(BackupSettings.get_solo().latest_backup)
        self.assertFalse(create_backup_mock.called)

        # Should not do anything.
        dsmr_backup.services.backup.check()
        self.assertFalse(create_backup_mock.called)

        backup_settings.latest_backup = now - timezone.timedelta(days=1)
        backup_settings.save()

        # Should be fine to backup now.
        dsmr_backup.services.backup.check()
        self.assertTrue(create_backup_mock.called)

    @mock.patch('dsmr_backup.services.backup.create')
    @mock.patch('django.utils.timezone.now')
    def test_check_backup_time_restriction(self, now_mock, create_backup_mock):
        """ Test whether backups are restricted by user's backup time preference. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1, hour=1, minute=5))

        now = timezone.localtime(timezone.now())
        backup_settings = BackupSettings.get_solo()
        backup_settings.latest_backup = now - timezone.timedelta(days=1)
        backup_settings.backup_time = (now + timezone.timedelta(seconds=15)).time()
        backup_settings.save()

        # Should not do anything, we should backup a minute from now.
        self.assertFalse(create_backup_mock.called)
        dsmr_backup.services.backup.check()
        self.assertFalse(create_backup_mock.called)

        # Should be fine to backup now. Passed prefered time of user.
        backup_settings.backup_time = now.time()
        backup_settings.save()

        dsmr_backup.services.backup.check()
        self.assertTrue(create_backup_mock.called)

    def test_get_backup_directory(self):
        # Default.
        self.assertEqual(
            dsmr_backup.services.backup.get_backup_directory(),
            os.path.join(settings.BASE_DIR, '..', 'backups/')
        )

        # Custom.
        FOLDER = '/var/tmp/test-dsmr'
        backup_settings = BackupSettings.get_solo()
        backup_settings.folder = FOLDER
        backup_settings.save()

        self.assertEqual(
            dsmr_backup.services.backup.get_backup_directory(),
            os.path.join(FOLDER)
        )

    @mock.patch('subprocess.Popen')
    @mock.patch('dsmr_backup.services.backup.compress')
    def test_create(self, compress_mock, subprocess_mock):
        FOLDER = '/var/tmp/test-dsmr'
        backup_settings = BackupSettings.get_solo()
        backup_settings.folder = FOLDER
        backup_settings.save()

        self.assertFalse(compress_mock.called)
        self.assertFalse(subprocess_mock.called)
        self.assertIsNone(BackupSettings.get_solo().latest_backup)
        self.assertTrue(BackupSettings.get_solo().compress)

        dsmr_backup.services.backup.create()
        self.assertTrue(compress_mock.called)
        self.assertTrue(subprocess_mock.called)

        self.assertIsNotNone(BackupSettings.get_solo().latest_backup)
        shutil.rmtree(FOLDER)

    @mock.patch('subprocess.Popen')
    @mock.patch('dsmr_backup.services.backup.compress')
    def test_create_without_compress(self, compress_mock, subprocess_mock):
        backup_settings = BackupSettings.get_solo()
        backup_settings.compress = False
        backup_settings.save()

        self.assertFalse(compress_mock.called)
        self.assertFalse(subprocess_mock.called)
        self.assertIsNone(BackupSettings.get_solo().latest_backup)
        self.assertFalse(BackupSettings.get_solo().compress)

        dsmr_backup.services.backup.create()
        self.assertFalse(compress_mock.called)
        self.assertTrue(subprocess_mock.called)

        self.assertIsNotNone(BackupSettings.get_solo().latest_backup)

    def test_compress(self):
        TEST_STRING = b'TestTestTest-1234567890'
        # Temp file without automtic deletion, as compress() should do that as well.
        source_file = tempfile.NamedTemporaryFile(delete=False)
        self.assertTrue(os.path.exists(source_file.name))
        gzip_file = '{}.gz'.format(source_file.name)

        source_file.write(TEST_STRING)
        source_file.flush()
        self.assertFalse(os.path.exists(gzip_file))

        # Compress should drop old file and create a new one.
        dsmr_backup.services.backup.compress(source_file.name)
        self.assertFalse(os.path.exists(source_file.name))
        self.assertTrue(os.path.exists(gzip_file))

        # Decompress and verify content.
        with gzip.open(gzip_file) as file_handle:
            file_content = file_handle.read()
            self.assertEqual(file_content, TEST_STRING)

        os.unlink(gzip_file)

    @mock.patch('dsmr_backup.services.dropbox.sync')
    def test_sync(self, dropbox_mock):
        self.assertFalse(dropbox_mock.called)

        # Should create initial backup.
        dsmr_backup.services.backup.sync()
        self.assertTrue(dropbox_mock.called)
