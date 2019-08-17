from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls.base import reverse
from django.utils import timezone
from django.conf import settings

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backup.models.settings import DropboxSettings, BackupSettings


class TestAdmin(TestCase):
    """ Test whether views render at all. """
    VIEWS = (
        'admin:dsmr_backup_backupsettings_changelist',
        'admin:dsmr_backup_dropboxsettings_changelist',
        'admin:dsmr_backup_emailbackupsettings_changelist',
    )

    def setUp(self):
        username = 'testuser'
        password = 'passwd'
        User.objects.create_superuser(username, 'unknown@localhost', password)

        self.client = Client()
        self.client.login(username=username, password=password)

    def test_admin(self):
        for current in self.VIEWS:
            response = self.client.get(reverse(current))
            self.assertEqual(response.status_code, 200)

    @mock.patch('django.utils.timezone.now')
    def test_reschedule_backup(self, now_mock):
        URL = reverse('admin:dsmr_backup_backupsettings_changelist')
        now_mock.return_value = timezone.make_aware(timezone.datetime(2019, 1, 1))  # Lock time

        BackupSettings.get_solo()
        BackupSettings.objects.all().update(latest_backup=timezone.now())
        self.assertFalse(BackupSettings.objects.filter(latest_backup__isnull=True).exists())

        # Just posting should reset it. NOTE: To apply settings, form params must validate!
        response = self.client.post(URL, data=dict(
            backup_time='06:00:00',
            folder='backups/'
        ))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(BackupSettings.objects.filter(latest_backup__isnull=True).exists())

    @mock.patch('django.utils.timezone.now')
    def test_reschedule_dropbox_sync(self, now_mock):
        URL = reverse('admin:dsmr_backup_dropboxsettings_changelist')
        now_mock.return_value = timezone.make_aware(timezone.datetime(2019, 1, 1))  # Lock time

        DropboxSettings.get_solo()
        DropboxSettings.objects.all().update(next_sync=timezone.now() + timezone.timedelta(hours=1))
        self.assertFalse(DropboxSettings.objects.filter(next_sync__lte=timezone.now()).exists())

        # Just posting should reset it.
        response = self.client.post(URL)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(DropboxSettings.objects.filter(next_sync__lte=timezone.now()).exists())

    def test_reschedule_email_backup(self):
        URL = reverse('admin:dsmr_backup_emailbackupsettings_changelist')

        ScheduledProcess.objects.all().update(planned=timezone.now() + timezone.timedelta(hours=1))
        self.assertFalse(ScheduledProcess.objects.filter(
            module=settings.DSMRREADER_MODULE_EMAIL_BACKUP,
            planned__lt=timezone.now()).exists()
        )

        # Just posting should reset it.
        response = self.client.post(URL)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ScheduledProcess.objects.filter(
            module=settings.DSMRREADER_MODULE_EMAIL_BACKUP,
            planned__lt=timezone.now()).exists()
        )
