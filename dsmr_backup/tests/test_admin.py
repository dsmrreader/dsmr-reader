from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls.base import reverse
from django.utils import timezone
from django.conf import settings

from dsmr_backend.models.schedule import ScheduledProcess


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

    def test_reschedule_process(self):
        REVERSE = 'admin:dsmr_backup_emailbackupsettings_changelist'

        ScheduledProcess.objects.all().update(planned=timezone.now() + timezone.timedelta(hours=1))
        self.assertFalse(
            ScheduledProcess.objects.filter(
                module=settings.DSMRREADER_MODULE_EMAIL_BACKUP,
                planned__lt=timezone.now()
            ).exists()
        )

        # Default (no effect).
        response = self.client.post(reverse(REVERSE))
        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            ScheduledProcess.objects.filter(
                module=settings.DSMRREADER_MODULE_EMAIL_BACKUP,
                planned__lt=timezone.now()
            ).exists()
        )

        # OK.
        response = self.client.post(
            reverse(REVERSE),
            data=dict(reschedule_process='yes')
        )
        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            ScheduledProcess.objects.filter(
                module=settings.DSMRREADER_MODULE_EMAIL_BACKUP,
                planned__lt=timezone.now()
            ).exists()
        )
