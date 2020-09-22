from django.test import TestCase, override_settings
from django.utils import timezone

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backup.models.settings import DropboxSettings
from dsmr_dropbox.apps import check_dropbox_sync


class TestStatus(TestCase):
    def setUp(self):
        DropboxSettings.get_solo().update(
            access_token='1234',
            next_sync=timezone.now()
        )

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=1)
    def test_check_dropbox_sync_okay(self):
        self.assertIsNone(check_dropbox_sync())

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=0)
    def test_check_dropbox_sync_fail(self):
        self.assertIsInstance(check_dropbox_sync(), MonitoringStatusIssue)

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=0)
    def test_check_dropbox_sync_disabled(self):
        DropboxSettings.get_solo().update(
            access_token=None,
            next_sync=timezone.now() - timezone.timedelta(minutes=1)
        )
        self.assertIsNone(check_dropbox_sync())
