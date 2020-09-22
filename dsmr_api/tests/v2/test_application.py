from unittest import mock

import pytz
from django.conf import settings
from django.utils import timezone

from dsmr_api.tests.v2 import APIv2TestCase
from dsmr_backend.dto import MonitoringStatusIssue


class TestVersion(APIv2TestCase):
    def test_get(self):
        result = self._request('application-version')

        major, minor, patch = settings.DSMRREADER_RAW_VERSION[:3]
        self.assertEqual(result['version'], '{}.{}.{}'.format(major, minor, patch))


class TestMonitoring(APIv2TestCase):
    @mock.patch('dsmr_backend.services.backend.request_monitoring_status')
    def test_get(self, status_mock):
        status_mock.return_value = [MonitoringStatusIssue(
            'source',
            'description',
            timezone.datetime(2020, 1, 15, 12, 34, 56, 0, pytz.UTC)
        )]

        result = self._request('application-monitoring')

        self.assertEqual(result['problems'], 1)
        self.assertEqual(result['details'][0]['source'], 'source')
        self.assertEqual(result['details'][0]['description'], 'description')
        self.assertEqual(result['details'][0]['since'], '2020-01-15T13:34:56+01:00')
