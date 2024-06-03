from django.test import TestCase, override_settings
from django.utils import timezone

from dsmr_backend.apps import check_scheduled_processes
from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backend.models.schedule import ScheduledProcess


class TestStatus(TestCase):
    def setUp(self):
        ScheduledProcess.objects.all().update(
            active=True, planned=timezone.now() - timezone.timedelta(minutes=1)
        )
        self.assertEqual(ScheduledProcess.objects.all().count(), 11)

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=2)
    def test_check_scheduled_processes_okay(self):
        self.assertEqual(check_scheduled_processes(), [])

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=0)
    def test_check_scheduled_processes_fail(self):
        result = check_scheduled_processes()
        self.assertEqual(len(result), 11)
        [self.assertIsInstance(x, MonitoringStatusIssue) for x in result]

    @override_settings(DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES=0)
    def test_check_scheduled_processes_disabled(self):
        ScheduledProcess.objects.all().update(active=False)
        self.assertEqual(check_scheduled_processes(), [])
