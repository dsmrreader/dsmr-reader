import tempfile
import gzip
import os
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_backup.models.settings import BackupSettings
import dsmr_backup.services.backup


class TestBackupServices(CallCommandStdoutMixin, TestCase):
    @mock.patch('dsmr_backup.services.backup.create')
    def test_check_initial(self, create_backup_mock):
        """ Test whether a initial backup is created immediately. """
        self.assertFalse(create_backup_mock.called)

        # Should create initial backup.
        dsmr_backup.services.backup.check()
        self.assertTrue(create_backup_mock.called)

    @mock.patch('dsmr_backup.services.backup.create')
    def test_check_interval_restriction(self, create_backup_mock):
        """ Test whether backups are restricted by an interval. """
        # Fake latest backup.
        backup_settings = BackupSettings.get_solo()
        backup_settings.latest_backup = timezone.now()
        backup_settings.save()

        self.assertIsNotNone(BackupSettings.get_solo().latest_backup)
        self.assertFalse(create_backup_mock.called)

        # Should not do anything.
        dsmr_backup.services.backup.check()
        self.assertFalse(create_backup_mock.called)

    @mock.patch('dsmr_backup.services.backup.create')
    def test_check_backup_time_restriction(self, create_backup_mock):
        """ Test whether backups are restricted by the user's backup time preference. """
        # Fake latest backup, long time ago.
        backup_settings = BackupSettings.get_solo()
        backup_settings.latest_backup = timezone.now() - timezone.timedelta(weeks=1)
        backup_settings.save()
        self.assertIsNotNone(BackupSettings.get_solo().latest_backup)

        # Fake the user's preference. BUG BUG: This might fail when test run just before midnight.
        backup_settings.backup_time = (timezone.now() + timezone.timedelta(minutes=1)).time()
        backup_settings.save()

        self.assertFalse(create_backup_mock.called)

        # Should not do anything.
        dsmr_backup.services.backup.check()
        self.assertFalse(create_backup_mock.called)

    def test_get_backup_directory(self):
        self.assertEqual(
            dsmr_backup.services.backup.get_backup_directory(),
            os.path.join(settings.BASE_DIR, '..', settings.DSMR_BACKUP_DIRECTORY)
        )

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
