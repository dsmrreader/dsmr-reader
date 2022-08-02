from unittest import mock

from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_backend.models.schedule import ScheduledProcess
import dsmr_backup.services.email
from dsmr_backup.models.settings import EmailBackupSettings


class TestEmailServices(InterceptCommandStdoutMixin, TestCase):
    @mock.patch("dsmr_backup.services.backup.create_partial")
    @mock.patch("dsmr_backend.services.email.send")
    def test_run(self, send_mock, create_backup_mock):
        sp = ScheduledProcess.objects.create(name="Test", module="fake.module")

        self.assertFalse(create_backup_mock.called)
        self.assertFalse(send_mock.called)

        dsmr_backup.services.email.run(scheduled_process=sp)

        self.assertFalse(create_backup_mock.called)
        self.assertFalse(send_mock.called)

        # Now with settings enabled.
        EmailBackupSettings.objects.all().update(
            interval=EmailBackupSettings.INTERVAL_DAILY
        )

        dsmr_backup.services.email.run(scheduled_process=sp)

        self.assertTrue(create_backup_mock.called)
        self.assertTrue(send_mock.called)
