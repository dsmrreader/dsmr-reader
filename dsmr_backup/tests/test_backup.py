from unittest import mock
import shutil
import os
import io

from django.db import connection
from django.test import TestCase
from django.utils import timezone
from django.conf import settings

from dsmr_backend.tests.mixins import InterceptStdoutMixin
from dsmr_backup.models.settings import BackupSettings
from dsmr_frontend.models.message import Notification
from dsmr_stats.models.statistics import DayStatistics
import dsmr_backup.services.backup


class TestBackupServices(InterceptStdoutMixin, TestCase):
    def setUp(self):
        BackupSettings.get_solo()

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    def test_check_backups_disabled(self, create_full_mock, create_partial_mock):
        backup_settings = BackupSettings.get_solo()
        backup_settings.daily_backup = False
        backup_settings.save()

        self.assertFalse(BackupSettings.get_solo().daily_backup)
        self.assertFalse(create_partial_mock.called)
        self.assertFalse(create_full_mock.called)
        self.assertIsNone(BackupSettings.get_solo().latest_backup)

        # Should not do anything.
        dsmr_backup.services.backup.check()
        self.assertFalse(create_partial_mock.called)
        self.assertFalse(create_full_mock.called)
        self.assertIsNone(BackupSettings.get_solo().latest_backup)

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    @mock.patch('django.utils.timezone.now')
    def test_check_initial(self, now_mock, create_full_mock, create_partial_mock):
        """ Test whether a initial backup is created immediately. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1, hour=18))
        self.assertFalse(create_partial_mock.called)
        self.assertFalse(create_full_mock.called)
        self.assertIsNone(BackupSettings.get_solo().latest_backup)

        # Should create initial backup.
        dsmr_backup.services.backup.check()
        self.assertTrue(create_partial_mock.called)
        self.assertTrue(create_full_mock.called)
        self.assertIsNotNone(BackupSettings.get_solo().latest_backup)

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    @mock.patch('django.utils.timezone.now')
    def test_check_backup_folders(self, now_mock, create_full_mock, create_partial_mock):
        """ Test whether the backups use the expected folders. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1, hour=18))
        base_dir = dsmr_backup.services.backup.get_backup_directory()

        # Should create initial backup.
        dsmr_backup.services.backup.check()

        _, kwargs = create_partial_mock.call_args_list[0]
        self.assertEqual(kwargs['folder'], os.path.join(base_dir, 'archive/2016/01'))

        _, kwargs = create_full_mock.call_args_list[0]
        self.assertEqual(kwargs['folder'], base_dir)

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    @mock.patch('django.utils.timezone.now')
    def test_check_interval_restriction(self, now_mock, create_full_mock, create_partial_mock):
        """ Test whether backups are restricted by one backup per day. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1, hour=1, minute=5))

        # Fake latest backup.
        now = timezone.localtime(timezone.now())
        backup_settings = BackupSettings.get_solo()
        backup_settings.latest_backup = now
        backup_settings.backup_time = (now - timezone.timedelta(minutes=1)).time()
        backup_settings.save()

        self.assertIsNotNone(BackupSettings.get_solo().latest_backup)
        self.assertFalse(create_partial_mock.called)
        self.assertFalse(create_full_mock.called)

        # Should not do anything.
        dsmr_backup.services.backup.check()
        self.assertFalse(create_partial_mock.called)
        self.assertFalse(create_full_mock.called)

        backup_settings.latest_backup = now - timezone.timedelta(days=1)
        backup_settings.save()

        # Should be fine to backup now.
        dsmr_backup.services.backup.check()
        self.assertTrue(create_partial_mock.called)
        self.assertTrue(create_full_mock.called)

    @mock.patch('dsmr_backup.services.backup.create_partial')
    @mock.patch('dsmr_backup.services.backup.create_full')
    @mock.patch('django.utils.timezone.now')
    def test_check_backup_time_restriction(self, now_mock, create_full_mock, create_partial_mock):
        """ Test whether backups are restricted by user's backup time preference. """
        now_mock.return_value = timezone.make_aware(timezone.datetime(2016, 1, 1, hour=1, minute=5))

        now = timezone.localtime(timezone.now())
        backup_settings = BackupSettings.get_solo()
        backup_settings.latest_backup = now - timezone.timedelta(days=1)
        backup_settings.backup_time = (now + timezone.timedelta(seconds=15)).time()
        backup_settings.save()

        # Should not do anything, we should backup a minute from now.
        self.assertFalse(create_partial_mock.called)
        self.assertFalse(create_full_mock.called)
        dsmr_backup.services.backup.check()
        self.assertFalse(create_partial_mock.called)
        self.assertFalse(create_full_mock.called)

        # Should be fine to backup now. Passed prefered time of user.
        backup_settings.backup_time = now.time()
        backup_settings.save()

        dsmr_backup.services.backup.check()
        self.assertTrue(create_partial_mock.called)
        self.assertTrue(create_full_mock.called)

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

        # Specify.
        dir = dsmr_backup.services.backup.get_backup_directory(backup_directory='////var/tmp/')
        self.assertEqual(dir, '/var/tmp')

    @mock.patch('subprocess.run')
    @mock.patch('dsmr_backup.services.backup.on_backup_failed')
    def test_create_full(self, on_backup_failed_mock, subprocess_mock):
        FOLDER = '/var/tmp/test-dsmr/'
        BackupSettings.objects.all().update(folder=FOLDER)
        process_handle = mock.MagicMock()
        type(process_handle).returncode = mock.PropertyMock(return_value=0)
        type(process_handle).stdout = mock.PropertyMock(return_value=b'Test content')
        subprocess_mock.return_value = process_handle

        self.assertFalse(subprocess_mock.called)
        self.assertFalse(on_backup_failed_mock.called)

        dsmr_backup.services.backup.create_full(
            folder=dsmr_backup.services.backup.get_backup_directory()
        )
        self.assertTrue(subprocess_mock.called)
        self.assertFalse(on_backup_failed_mock.called)
        subprocess_mock.reset_mock()

        # Test again, different branch coverage, as folder now exists.
        dsmr_backup.services.backup.create_full(
            folder=dsmr_backup.services.backup.get_backup_directory()
        )

        self.assertTrue(subprocess_mock.called)

        # Test unexpected exitcode.
        process_handle = mock.MagicMock()
        type(process_handle).returncode = mock.PropertyMock(return_value=-1)
        type(process_handle).stdout = mock.PropertyMock(return_value=b'Test content')
        subprocess_mock.return_value = process_handle

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

    @mock.patch('subprocess.run')
    def test_create_partial(self, subprocess_mock):
        if connection.vendor != 'postgres':  # pragma: no cover
            return self.skipTest(reason='Only PostgreSQL supported')

        FOLDER = '/var/tmp/test-dsmr'
        BackupSettings.objects.all().update(folder=FOLDER)

        self.assertFalse(subprocess_mock.called)
        self.assertIsNone(BackupSettings.get_solo().latest_backup)

        dsmr_backup.services.backup.create_partial(
            folder=dsmr_backup.services.backup.get_backup_directory(),
            models_to_backup=(DayStatistics, )
        )
        self.assertTrue(subprocess_mock.called)
        shutil.rmtree(FOLDER)

    @mock.patch('dsmr_dropbox.services.sync')
    def test_sync(self, dropbox_mock):
        self.assertFalse(dropbox_mock.called)

        # Should sync initial backup remotely.
        dsmr_backup.services.backup.sync()
        self.assertTrue(dropbox_mock.called)
