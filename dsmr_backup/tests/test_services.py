import tempfile
import gzip
import os
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from dsmr_backend.tests.mixins import CallCommandStdoutMixin
from dsmr_backup.models.settings import BackupSettings, DropboxSettings
import dsmr_backup.services.backup
import dsmr_backup.services.dropbox


class TestBackupServices(CallCommandStdoutMixin, TestCase):
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
    def test_check_initial(self, create_backup_mock):
        """ Test whether a initial backup is created immediately. """
        self.assertFalse(create_backup_mock.called)

        # Should create initial backup.
        dsmr_backup.services.backup.check()
        self.assertTrue(create_backup_mock.called)

    @mock.patch('dsmr_backup.services.backup.create')
    def test_check_interval_restriction(self, create_backup_mock):
        """ Test whether backups are restricted by one backup per day. """
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
    def test_check_backup_time_restriction(self, create_backup_mock):
        """ Test whether backups are restricted by user's backup time preference. """
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
        self.assertEqual(
            dsmr_backup.services.backup.get_backup_directory(),
            os.path.join(settings.BASE_DIR, '..', settings.DSMR_BACKUP_DIRECTORY)
        )

    @mock.patch('subprocess.Popen')
    @mock.patch('dsmr_backup.services.backup.compress')
    def test_create(self, compress_mock, subprocess_mock):
        self.assertFalse(compress_mock.called)
        self.assertFalse(subprocess_mock.called)
        self.assertIsNone(BackupSettings.get_solo().latest_backup)

        dsmr_backup.services.backup.create()
        self.assertTrue(compress_mock.called)
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


class TestDropboxServices(CallCommandStdoutMixin, TestCase):
    def setUp(self):
        dropbox_settings = DropboxSettings.get_solo()
        dropbox_settings.access_token = 'FAKE'
        dropbox_settings.save()

    @mock.patch('dsmr_backup.services.dropbox.upload_chunked')
    def test_sync_disabled(self, upload_chunked_mock):
        dropbox_settings = DropboxSettings.get_solo()
        dropbox_settings.access_token = None
        dropbox_settings.save()

        self.assertFalse(upload_chunked_mock.called)

        dsmr_backup.services.dropbox.sync()
        self.assertFalse(upload_chunked_mock.called)

    @mock.patch('dsmr_backup.services.dropbox.upload_chunked')
    def test_sync(self, upload_chunked_mock):
        old_latest_sync = timezone.now() - timezone.timedelta(weeks=1)
        dropbox_settings = DropboxSettings.get_solo()
        dropbox_settings.latest_sync = old_latest_sync
        dropbox_settings.save()

        self.assertFalse(upload_chunked_mock.called)
        self.assertIsNotNone(DropboxSettings.get_solo().access_token)

        dsmr_backup.services.dropbox.sync()
        self.assertTrue(upload_chunked_mock.called)
        self.assertNotEqual(DropboxSettings.get_solo().latest_sync, old_latest_sync)

    @mock.patch('dsmr_backup.services.backup.get_backup_directory')
    def test_sync_latest_sync(self, get_backup_directory_mock):
        """ Test whether syncs are limited to intervals. """
        dropbox_settings = DropboxSettings.get_solo()
        dropbox_settings.latest_sync = timezone.now() + timezone.timedelta(minutes=1)
        dropbox_settings.save()

        self.assertFalse(get_backup_directory_mock.called)

        dsmr_backup.services.dropbox.sync()
        self.assertFalse(get_backup_directory_mock.called)

    @mock.patch('dsmr_backup.services.backup.get_backup_directory')
    @mock.patch('dsmr_backup.services.dropbox.upload_chunked')
    def test_sync_last_modified(self, upload_chunked_mock, get_backup_directory_mock):
        """ Test whether syncs are skipped when file was not modified. """
        dropbox_settings = DropboxSettings.get_solo()
        dropbox_settings.latest_sync = timezone.now() - timezone.timedelta(weeks=1)
        dropbox_settings.save()

        with tempfile.TemporaryDirectory() as temp_dir:
            get_backup_directory_mock.return_value = temp_dir
            temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
            temp_file.write(b'Meh.')
            temp_file.flush()

            # 1420070400: 01 Jan 2015 00:00:00 GMT
            os.utime(temp_file.name, times=(1420070400, 1420070400))
            self.assertFalse(upload_chunked_mock.called)

            # File should be ignored, as it's modification timestamp is before latest sync.
            dsmr_backup.services.dropbox.sync()
            self.assertFalse(upload_chunked_mock.called)

    @mock.patch('dropbox.client.DropboxClient.get_chunked_uploader')
    def test_upload_chunked(self, chunked_uploader_mock):
        DATA = b'Lots of data.'
        uploader_mock = mock.MagicMock()
        type(uploader_mock).offset = mock.PropertyMock(side_effect=[0, 5, 10, len(DATA), len(DATA)])
        chunked_uploader_mock.return_value = uploader_mock

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(DATA)
            temp_file.flush()

            dsmr_backup.services.dropbox.upload_chunked(temp_file.name)
            self.assertTrue(uploader_mock.finish.called)
