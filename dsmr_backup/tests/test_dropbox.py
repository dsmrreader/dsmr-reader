import tempfile
import os
from unittest import mock

from django.test import TestCase
from django.utils import timezone
from django.conf import settings
import dropbox

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_backup.models.settings import DropboxSettings
from dsmr_frontend.models.message import Notification
import dsmr_backup.services.dropbox


class TestDropboxServices(InterceptStdoutMixin, TestCase):
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
    @mock.patch('django.utils.timezone.now')
    def test_sync_initial(self, now_mock, upload_chunked_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))

        # Initial project state.
        dropbox_settings = DropboxSettings.get_solo()
        dropbox_settings.next_sync = None
        dropbox_settings.save()

        dsmr_backup.services.dropbox.sync()
        self.assertTrue(upload_chunked_mock.called)

    @mock.patch('dsmr_backup.services.dropbox.upload_chunked')
    @mock.patch('django.utils.timezone.now')
    def test_sync(self, now_mock, upload_chunked_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))

        old_next_sync = timezone.now() - timezone.timedelta(weeks=1)
        dropbox_settings = DropboxSettings.get_solo()
        dropbox_settings.next_sync = old_next_sync
        dropbox_settings.save()

        self.assertFalse(upload_chunked_mock.called)
        self.assertIsNotNone(DropboxSettings.get_solo().access_token)

        dsmr_backup.services.dropbox.sync()
        self.assertTrue(upload_chunked_mock.called)
        self.assertNotEqual(DropboxSettings.get_solo().next_sync, old_next_sync)

    @mock.patch('dsmr_backup.services.backup.get_backup_directory')
    @mock.patch('django.utils.timezone.now')
    def test_sync_latest_sync(self, now_mock, get_backup_directory_mock):
        """ Test whether syncs are limited to intervals. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))

        dropbox_settings = DropboxSettings.get_solo()
        dropbox_settings.next_sync = timezone.now() + timezone.timedelta(minutes=1)
        dropbox_settings.save()

        self.assertFalse(get_backup_directory_mock.called)

        dsmr_backup.services.dropbox.sync()
        self.assertFalse(get_backup_directory_mock.called)

    @mock.patch('dsmr_backup.services.backup.get_backup_directory')
    @mock.patch('dsmr_backup.services.dropbox.upload_chunked')
    @mock.patch('django.utils.timezone.now')
    def test_sync_last_modified(self, now_mock, upload_chunked_mock, get_backup_directory_mock):
        """ Test whether syncs are skipped when file was not modified. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))

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

    @mock.patch('dsmr_backup.services.dropbox.upload_chunked')
    @mock.patch('django.utils.timezone.now')
    def test_sync_insufficient_space(self, now_mock, upload_chunked_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2000, 1, 1))

        # Crash the party, no more space available!
        upload_chunked_mock.side_effect = dropbox.exceptions.ApiError(
            12345,
            "UploadError('path', UploadWriteFailed(reason=WriteError('insufficient_space', None), ...)",
            'x',
            'y'
        )

        Notification.objects.all().delete()
        self.assertEqual(Notification.objects.count(), 0)

        with self.assertRaises(dropbox.exceptions.ApiError):
            dsmr_backup.services.dropbox.sync()

        # Warning message should be created and next sync should be skipped ahead.
        self.assertEqual(Notification.objects.count(), 1)
        self.assertGreater(
            DropboxSettings.get_solo().next_sync, timezone.now() + timezone.timedelta(
                hours=settings.DSMRREADER_DROPBOX_ERROR_INTERVAL - 1
            )
        )

    @mock.patch('dsmr_backup.services.dropbox.upload_chunked')
    @mock.patch('django.utils.timezone.now')
    def test_sync_invalid_access_token(self, now_mock, upload_chunked_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2000, 1, 1))

        # Crash the party, no more space available!
        upload_chunked_mock.side_effect = dropbox.exceptions.AuthError(
            12345,
            "AuthError('xxxxxxxxxxxxxxxxxxxxxxxx', AuthError('invalid_access_token', None))"
        )

        Notification.objects.all().delete()
        self.assertEqual(Notification.objects.count(), 0)

        with self.assertRaises(dropbox.exceptions.AuthError):
            dsmr_backup.services.dropbox.sync()

        # Warning message should be created and credetials should be wiped.
        dropbox_settings = DropboxSettings.get_solo()
        self.assertEqual(Notification.objects.count(), 1)
        self.assertIsNone(dropbox_settings.access_token)
        self.assertEqual(dropbox_settings.latest_sync, timezone.now())
        self.assertIsNone(dropbox_settings.next_sync)

    @mock.patch('dropbox.Dropbox.files_upload')
    @mock.patch('dropbox.Dropbox.files_upload_session_start')
    @mock.patch('dropbox.Dropbox.files_upload_session_append')
    @mock.patch('dropbox.Dropbox.files_upload_session_finish')
    def test_upload_chunked(self, session_finish_mock, session_append_mock, session_start_mock, files_upload_mock):
        DATA = b'Lots of data.'
        session_start_result = mock.MagicMock()
        type(session_start_result).session_id = mock.PropertyMock(side_effect=['session-xxxxx'])
        session_start_mock.return_value = session_start_result

        self.assertFalse(files_upload_mock.called)
        self.assertFalse(session_start_mock.called)
        self.assertFalse(session_append_mock.called)
        self.assertFalse(session_finish_mock.called)

        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(DATA)
            temp_file.flush()

            dsmr_backup.services.dropbox.upload_chunked(temp_file.name)

        # Only small file upload should be called.
        self.assertTrue(files_upload_mock.called)
        self.assertFalse(session_start_mock.called)
        self.assertFalse(session_append_mock.called)
        self.assertFalse(session_finish_mock.called)

        # Large file upload (> 2 MB chunks).
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(DATA * 2 * 1024 * 1024)
            temp_file.flush()

            dsmr_backup.services.dropbox.upload_chunked(temp_file.name)

        self.assertTrue(session_start_mock.called)
        self.assertTrue(session_append_mock.called)
        self.assertTrue(session_finish_mock.called)
