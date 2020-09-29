from unittest import mock

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_backend.models.schedule import ScheduledProcess
import dsmr_backend.services.update_checker
import dsmr_backend.services.schedule
import dsmr_backend.signals


class TestUpdateChecker(InterceptCommandStdoutMixin, TestCase):
    schedule_process = None

    def setUp(self):
        self.schedule_process = ScheduledProcess.objects.get(module=settings.DSMRREADER_MODULE_AUTO_UPDATE_CHECKER)
        self.schedule_process.update(active=True, planned=timezone.make_aware(timezone.datetime(2010, 1, 1)))

    @mock.patch('dsmr_backend.services.backend.is_latest_version')
    @mock.patch('django.utils.timezone.now')
    def test_no_update(self, now_mock, is_latest_version_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2010, 1, 1))
        is_latest_version_mock.return_value = True

        dsmr_backend.services.update_checker.run(self.schedule_process)

        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(days=7))

    @mock.patch('dsmr_backend.services.backend.is_latest_version')
    @mock.patch('dsmr_frontend.services.display_dashboard_message')
    @mock.patch('django.utils.timezone.now')
    def test_has_update(self, now_mock, display_dashboard_message_mock, is_latest_version_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2010, 1, 1))
        is_latest_version_mock.return_value = False

        dsmr_backend.services.update_checker.run(self.schedule_process)
        self.assertTrue(display_dashboard_message_mock.called)

        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(days=7))

    @mock.patch('dsmr_backend.services.backend.is_latest_version')
    @mock.patch('django.utils.timezone.now')
    def test_exception(self, now_mock, is_latest_version_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2010, 1, 1))
        is_latest_version_mock.side_effect = IOError('Request failed')

        dsmr_backend.services.update_checker.run(self.schedule_process)

        self.schedule_process.refresh_from_db()
        self.assertEqual(self.schedule_process.planned, timezone.now() + timezone.timedelta(hours=1))
