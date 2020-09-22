from django.test import TestCase, override_settings
from django.utils import timezone

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_pvoutput.apps import check_pvoutput_sync
from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings


class TestStatus(TestCase):
    def setUp(self):
        PVOutputAddStatusSettings.get_solo().update(
            export=True,
            next_export=timezone.now()
        )

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=1)
    def test_check_pvoutput_sync_okay(self):
        self.assertIsNone(check_pvoutput_sync())

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=0)
    def test_check_pvoutput_sync_fail(self):
        self.assertIsInstance(check_pvoutput_sync(), MonitoringStatusIssue)

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=0)
    def test_check_pvoutput_sync_disabled(self):
        PVOutputAddStatusSettings.get_solo().update(
            export=False,
            next_export=timezone.now() - timezone.timedelta(minutes=1)
        )
        self.assertIsNone(check_pvoutput_sync())
