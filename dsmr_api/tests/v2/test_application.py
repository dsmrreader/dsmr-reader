from unittest import mock

from django.utils import timezone
from django.conf import settings

from dsmr_api.tests.v2 import APIv2TestCase


class TestVersion(APIv2TestCase):
    def test_get(self):
        result = self._request('application-version')

        major, minor, patch = settings.DSMRREADER_RAW_VERSION[:3]
        self.assertEqual(result['version'], '{}.{}.{}'.format(major, minor, patch))


class TestStatus(APIv2TestCase):
    fixtures = [
        'dsmr_api/test_dsmrreading.json',
        'dsmr_api/test_day_statistics.json',
        'dsmr_api/test_gas_consumption.json',
        'dsmr_api/test_electricity_consumption.json',
    ]

    @mock.patch('django.utils.timezone.now')
    def test_get(self, now_mock):
        now_mock.return_value = timezone.make_aware(timezone.datetime(2017, 1, 1))

        result = self._request('application-status')

        self.assertIn('capabilities', result)
        self.assertIn('electricity', result)
        self.assertIn('gas', result)
        self.assertIn('readings', result)
        self.assertIn('statistics', result)

        self.assertTrue(result['capabilities']['any'])
        self.assertTrue(result['capabilities']['electricity'])
        self.assertFalse(result['capabilities']['electricity_returned'])
        self.assertTrue(result['capabilities']['gas'])
        self.assertFalse(result['capabilities']['multi_phases'])

        self.assertEqual(result['readings']['unprocessed']['count'], 3)
        self.assertEqual(result['readings']['unprocessed']['seconds_since'], 15829200)
        self.assertEqual(result['readings']['seconds_since'], 15822000)
        self.assertEqual(result['readings']['latest'], '2016-07-01T20:00:00Z')

        self.assertEqual(result['electricity']['latest'], '2015-12-15T01:01:00Z')
        self.assertEqual(result['electricity']['minutes_since'], 551399)

        self.assertEqual(result['gas']['latest'], '2015-12-13T02:00:00Z')
        self.assertEqual(result['gas']['hours_since'], 9237)

        self.assertEqual(result['statistics']['latest'], '2015-12-17')
        self.assertEqual(result['statistics']['days_since'], 381)
        from pprint import pprint
        pprint(result, indent=4)
