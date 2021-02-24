from datetime import time
from unittest import mock
import tempfile
import shutil
import gzip
import os
import io

from django.db import connection
from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_backup.models.settings import BackupSettings
from dsmr_frontend.models.message import Notification
from dsmr_stats.models.statistics import DayStatistics
import dsmr_backup.services.backup


class TestBackupServices(InterceptCommandStdoutMixin, TestCase):
    def setUp(self):
        BackupSettings.get_solo()
        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_DAILY_BACKUP)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2000, 1, 1)))

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    def test_check_backups_disabled(self, create_full_mock, create_partial_mock):
        backup_settings = BackupSettings.get_solo()
        backup_settings.daily_backup = False
        backup_settings.save()  # Post save signal.

        self.schedule_process.refresh_from_db()
        self.assertFalse(self.schedule_process.active)

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    @mock.patch('django.utils.timezone.now')
    def test_check_initial(self, now_mock, create_full_mock, create_partial_mock):
        """ Test whether a initial backup is created immediately. """
        self.assertFalse(create_partial_mock.called)
        self.assertFalse(create_full_mock.called)

        # Partials only run on mondays (Sunday now)
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 3, hour=18))
        dsmr_backup.services.backup.run(self.schedule_process)
        self.assertFalse(create_partial_mock.called)
        self.assertTrue(create_full_mock.called)

        create_partial_mock.reset_mock()
        create_full_mock.reset_mock()

        # Partials only run on mondays (Monday now)
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 4, hour=18))
        dsmr_backup.services.backup.run(self.schedule_process)
        self.assertTrue(create_partial_mock.called)
        self.assertTrue(create_full_mock.called)

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    @mock.patch('django.utils.timezone.now')
    def test_check_backup_folders(self, now_mock, create_full_mock, create_partial_mock):
        """ Test whether the backups use the expected folders. """
        # Partials only run on mondays (Monday now)
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 4, hour=18))
        base_dir = dsmr_backup.services.backup.get_backup_directory()

        # Should create initial backup.
        dsmr_backup.services.backup.run(self.schedule_process)

        _, kwargs = create_partial_mock.call_args_list[0]
        self.assertEqual(kwargs['folder'], os.path.join(base_dir, 'archive/2016/01'))

        _, kwargs = create_full_mock.call_args_list[0]
        self.assertEqual(kwargs['folder'], base_dir)

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    @mock.patch('django.utils.timezone.now')
    def test_rescheduling(self, now_mock, create_full_mock, create_partial_mock):
        """ Test scheduling after success. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2020, 1, 1, hour=12))

        backup_settings = BackupSettings.get_solo()
        backup_settings.backup_time = time(6, 0, 0)  # 6:00:00
        backup_settings.save()

        # Just run and check new planned timestamp.
        dsmr_backup.services.backup.run(self.schedule_process)
        print(self.schedule_process.planned)
        self.schedule_process.refresh_from_db()
        self.assertEqual(
            self.schedule_process.planned,
            timezone.make_aware(timezone.datetime(2020, 1, 2, hour=6))
        )

    def test_get_backup_directory(self):
        # Default.
        self.assertEqual(
            dsmr_backup.services.backup.get_backup_directory(),
            os.path.abspath(os.path.join(settings.BASE_DIR, '..', 'backups/'))
        )

        # Custom.
        FOLDER = '/var/tmp/test-dsmr'
        BackupSettings.objects.all().update(folder=FOLDER)

        self.assertEqual(
            dsmr_backup.services.backup.get_backup_directory(),
            os.path.join(FOLDER)
        )

    @mock.patch('subprocess.Popen')
    @mock.patch('dsmr_backup.services.backup.compress')
    @mock.patch('dsmr_backup.services.backup.on_backup_failed')
    def test_create_full(self, on_backup_failed_mock, compress_mock, subprocess_mock):
        FOLDER = '/var/tmp/test-dsmr/'
        BackupSettings.objects.all().update(folder=FOLDER)
        handle_mock = mock.MagicMock()
        handle_mock.returncode = 0
        subprocess_mock.return_value = handle_mock

        self.assertFalse(compress_mock.called)
        self.assertFalse(subprocess_mock.called)
        self.assertFalse(on_backup_failed_mock.called)

        dsmr_backup.services.backup.create_full(
            folder=dsmr_backup.services.backup.get_backup_directory()
        )
        self.assertTrue(compress_mock.called)
        self.assertTrue(subprocess_mock.called)
        self.assertFalse(on_backup_failed_mock.called)
        compress_mock.reset_mock()
        subprocess_mock.reset_mock()

        # Test again, different branch coverage, as folder now exists.
        dsmr_backup.services.backup.create_full(
            folder=dsmr_backup.services.backup.get_backup_directory()
        )

        self.assertTrue(compress_mock.called)
        self.assertTrue(subprocess_mock.called)

        # Test unexpected exitcode.
        handle_mock = mock.MagicMock()
        handle_mock.returncode = -1
        subprocess_mock.return_value = handle_mock

        dsmr_backup.services.backup.create_full(
            folder=dsmr_backup.services.backup.get_backup_directory()
        )
        self.assertTrue(on_backup_failed_mock.called)

        shutil.rmtree(FOLDER)

    def test_on_backup_failed(self):
        subprocess_mock = mock.MagicMock()
        subprocess_mock.stderr = io.StringIO('error')
        subprocess_mock.returncode = 0

        Notification.objects.all().delete()
        self.assertFalse(Notification.objects.exists())

        # Exception should be rainsed and message created.
        with self.assertRaises(IOError):
            dsmr_backup.services.backup.on_backup_failed(process_handle=subprocess_mock)

        self.assertTrue(Notification.objects.exists())

    @mock.patch('subprocess.Popen')
    @mock.patch('dsmr_backup.services.backup.compress')
    def test_create_partial(self, compress_mock, subprocess_mock):
        if connection.vendor != 'postgres':  # pragma: no cover
            return self.skipTest(reason='Only PostgreSQL supported')

        FOLDER = '/var/tmp/test-dsmr'
        BackupSettings.objects.all().update(folder=FOLDER)

        self.assertFalse(compress_mock.called)
        self.assertFalse(subprocess_mock.called)
        # self.assertIsNone(BackupSettings.get_solo().latest_backup)

        dsmr_backup.services.backup.create_partial(
            folder=dsmr_backup.services.backup.get_backup_directory(),
            models_to_backup=(DayStatistics, )
        )
        self.assertTrue(compress_mock.called)
        self.assertTrue(subprocess_mock.called)

        shutil.rmtree(FOLDER)

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
