import tempfile
import os
from unittest import mock

from django.test import TestCase, override_settings
from django.utils import timezone
from django.conf import settings
import dropbox

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_backup.models.settings import DropboxSettings
from dsmr_frontend.models.message import Notification
import dsmr_dropbox.services


class TestServices(InterceptCommandStdoutMixin, TestCase):
    def setUp(self):
        DropboxSettings.get_solo()
        DropboxSettings.objects.all().update(access_token='FAKE')

        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_DROPBOX_EXPORT)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

    @mock.patch('dsmr_dropbox.services.upload_chunked')
    @mock.patch('dropbox.Dropbox.files_get_metadata')
    def test_sync_disabled(self, _, upload_chunked_mock):
        DropboxSettings.objects.all().update(access_token=None)

        self.assertFalse(upload_chunked_mock.called)

        dsmr_dropbox.services.run(self.schedule_process)
        self.assertFalse(upload_chunked_mock.called)

    @mock.patch('dropbox.Dropbox.users_get_space_usage')
    @mock.patch('django.utils.timezone.now')
    def test_check_access_token(self, now_mock, users_get_space_usage_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 1, 1))

        for current_class in (dropbox.exceptions.BadInputError, dropbox.exceptions.AuthError):
            DropboxSettings.objects.all().update(access_token='invalid-token')
            users_get_space_usage_mock.side_effect = current_class(12345, "Some error")

            Notification.objects.all().delete()
            self.assertEqual(Notification.objects.count(), 0)

            with self.assertRaises(current_class):
                dsmr_dropbox.services.check_access_token(self.schedule_process, dropbox_access_token='dummy')

            # Warning message should be created and SP disabled.
            self.assertEqual(Notification.objects.count(), 1)
            self.schedule_process.refresh_from_db()
            self.assertFalse(self.schedule_process.active)
    #
    # @mock.patch('dsmr_dropbox.services.check_access_token')
    # @mock.patch('dsmr_dropbox.services.sync_file')
    # @mock.patch('dsmr_dropbox.services.should_sync_file')
    # @mock.patch('dropbox.Dropbox.files_get_metadata')
    # @mock.patch('django.utils.timezone.now')
    # def test_sync_initial(self, now_mock, _, should_mock, sync_file_mock, *mocks):
    #     now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
    #     should_mock.return_value = True
    #
    #     # Initial project state.
    #     DropboxSettings.objects.all().update(next_sync=None)
    #
    #     dsmr_dropbox.services.run(self.schedule_process)
    #     self.assertTrue(sync_file_mock.called)

    @mock.patch('dsmr_dropbox.services.check_access_token')
    @mock.patch('dsmr_dropbox.services.list_files_in_dir')
    @mock.patch('dsmr_dropbox.services.sync_file')
    @mock.patch('dsmr_dropbox.services.should_sync_file')
    @mock.patch('dropbox.Dropbox.files_get_metadata')
    @mock.patch('django.utils.timezone.now')
    def test_sync(self, now_mock, _, should_mock, sync_file_mock, list_files_in_dir_mock, *mocks):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1))
        should_mock.side_effect = [False, True]  # Both branches.
        list_files_in_dir_mock.return_value = ['/tmp/fake1', '/tmp/fake2']

        self.assertFalse(sync_file_mock.called)
        self.assertIsNotNone(DropboxSettings.get_solo().access_token)

        dsmr_dropbox.services.run(self.schedule_process)
        self.assertTrue(sync_file_mock.called)

        self.schedule_process.refresh_from_db()
        self.assertEqual(
            self.schedule_process.planned,
            timezone.make_aware(timezone.datetime(2016, 1, 1, hour=1))
        )

    @mock.patch('dsmr_dropbox.services.check_access_token')
    @mock.patch('dsmr_backup.services.backup.get_backup_directory')
    @mock.patch('dsmr_dropbox.services.upload_chunked')
    @mock.patch('dsmr_dropbox.services.calculate_content_hash')
    @mock.patch('dropbox.Dropbox.files_get_metadata')
    def test_sync_content_not_modified(self, files_get_metadata_mock, calculate_hash_mock, upload_chunked_mock,
                                       get_backup_directory_mock, *mocks):
        """ Test whether syncs are skipped when file was not modified. """
        HASH = 'abcdef123456'
        fake_metadata = mock.MagicMock()
        fake_metadata.content_hash = HASH
        files_get_metadata_mock.return_value = fake_metadata
        calculate_hash_mock.return_value = HASH

        with tempfile.TemporaryDirectory() as temp_dir:
            get_backup_directory_mock.return_value = temp_dir
            temp_file = tempfile.NamedTemporaryFile(dir=temp_dir, delete=False)
            temp_file.write(b'Meh.')
            temp_file.flush()

            # File should be ignored.
            dsmr_dropbox.services.run(self.schedule_process)
            self.assertFalse(upload_chunked_mock.called)
            upload_chunked_mock.reset_mock()

            # Again.
            self.schedule_process.delay(seconds=-1)

            # File should be synced when the content differs.
            calculate_hash_mock.return_value = reversed(HASH)
            dsmr_dropbox.services.run(self.schedule_process)
            self.assertTrue(upload_chunked_mock.called)

    @mock.patch('dsmr_dropbox.services.upload_chunked')
    @mock.patch('dsmr_dropbox.services.calculate_content_hash')
    @mock.patch('dropbox.Dropbox.files_get_metadata')
    @mock.patch('django.utils.timezone.now')
    def test_sync_insufficient_space(self, now_mock, _, __, upload_chunked_mock):
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
            dsmr_dropbox.services.sync_file(
                scheduled_process=self.schedule_process,
                dropbox_access_token='dummy-token',
                local_root_dir='/var/tmp/',
                abs_file_path='/var/tmp/fake'
            )

        # Warning message should be created and next sync should be skipped ahead.
        self.assertEqual(Notification.objects.count(), 1)
        self.schedule_process.refresh_from_db()
        self.assertGreater(
            self.schedule_process.planned,
            timezone.make_aware(timezone.datetime(2000, 1, 1, hour=settings.DSMRREADER_DROPBOX_ERROR_INTERVAL - 1))
        )

    @mock.patch('dsmr_dropbox.services.check_access_token')
    @mock.patch('dsmr_dropbox.services.upload_chunked')
    @mock.patch('dropbox.Dropbox.files_get_metadata')
    @mock.patch('os.stat')
    def test_sync_non_existing_remote_file(self, stat_mock, files_get_metadata_mock, upload_chunked_mock, *mocks):
        stat_result = mock.MagicMock()
        stat_result.st_size = 1234
        stat_mock.return_value = stat_result

        # Unknown file remote.
        files_get_metadata_mock.side_effect = dropbox.exceptions.ApiError(
            12345,
            "ApiError('xxx', ApiError('not_found', None))",
            'x',
            'y'
        )

        # This should continue sync, as the file is new on remote.
        dsmr_dropbox.services.run(self.schedule_process)
        self.assertTrue(files_get_metadata_mock.called)
        self.assertTrue(upload_chunked_mock.called)

        # Try again, different error, unexpected, but must be handled.
        files_get_metadata_mock.reset_mock()
        upload_chunked_mock.reset_mock()
        self.schedule_process.delay(seconds=-1)
        files_get_metadata_mock.side_effect = dropbox.exceptions.ApiError(
            67890,
            "ApiError('xxx', ApiError('other_error', None))",
            'x',
            'y'
        )

        # This should continue sync, as the error is unexpected.
        dsmr_dropbox.services.run(self.schedule_process)
        self.assertTrue(files_get_metadata_mock.called)
        self.assertFalse(upload_chunked_mock.called)

    @override_settings(DSMRREADER_DROPBOX_MAX_FILE_MODIFICATION_TIME=60)
    @mock.patch('time.time')
    @mock.patch('os.stat')
    def test_should_sync_file(self, stat_mock, time_mock):
        time_mock.return_value = 1500000100
        FILE = '/var/tmp/fake'

        # Skip empty file.
        stat_result = mock.MagicMock()
        stat_result.st_size = 0
        stat_result.st_mtime = 1500000000  # Start with 100s diff.
        stat_mock.return_value = stat_result

        self.assertFalse(dsmr_dropbox.services.should_sync_file(FILE))
        # Skip stale file.
        stat_result = mock.MagicMock()
        stat_result.st_size = 12345  # Not empty
        stat_result.st_mtime = 1500000000
        stat_mock.return_value = stat_result

        self.assertFalse(dsmr_dropbox.services.should_sync_file(FILE))

        # OK path.
        stat_result = mock.MagicMock()
        stat_result.st_size = 12345
        stat_result.st_mtime = 1500000090  # Within settings range (10s diff, 60s allowed)
        stat_mock.return_value = stat_result

        self.assertTrue(dsmr_dropbox.services.should_sync_file(FILE))

    @mock.patch('dropbox.Dropbox.files_upload')
    @mock.patch('dropbox.Dropbox.files_upload_session_start')
    @mock.patch('dropbox.Dropbox.files_upload_session_append_v2')
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

            dsmr_dropbox.services.upload_chunked(
                'dummy-token',
                temp_file.name,
                '/remote-path.ext'
            )

        # Only small file upload should be called.
        self.assertTrue(files_upload_mock.called)
        self.assertFalse(session_start_mock.called)
        self.assertFalse(session_append_mock.called)
        self.assertFalse(session_finish_mock.called)

        # Large file upload (> 2 MB chunks).
        with tempfile.NamedTemporaryFile() as temp_file:
            temp_file.write(DATA * 2 * 1024 * 1024)
            temp_file.flush()

            dsmr_dropbox.services.upload_chunked(
                'dummy-token',
                temp_file.name,
                '/remote-path.ext'
            )
        self.assertTrue(session_start_mock.called)
        self.assertTrue(session_append_mock.called)
        self.assertTrue(session_finish_mock.called)

    def test_calculate_content_hash(self):
        result = dsmr_dropbox.services.calculate_content_hash(
            os.path.join(os.path.dirname(__file__), 'dummy.txt')
        )
        self.assertEqual(result, '5b1cfae049eea4a702abd22437f54a775044dbc22cc99fa97c2dce68eb368b5a')
