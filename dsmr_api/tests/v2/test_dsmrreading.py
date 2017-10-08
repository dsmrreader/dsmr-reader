from dsmr_api.tests.v2 import APIv2TestCase
from dsmr_datalogger.models.reading import DsmrReading


class TestDsmrreading(APIv2TestCase):
    fixtures = ['dsmr_api/test_dsmrreading.json']

    def test_get(self):
        resultset = self._request('dsmrreading')
        self.assertEqual(resultset['count'], 3)
        self.assertEqual(resultset['results'][0]['id'], 1)
        self.assertEqual(resultset['results'][1]['id'], 2)
        self.assertEqual(resultset['results'][2]['id'], 3)

        # Limit.
        resultset = self._request('dsmrreading', data={'limit': 1})
        self.assertEqual(resultset['count'], 3)
        self.assertEqual(len(resultset['results']), 1)

        # Sort.
        resultset = self._request('dsmrreading', data={'ordering': '-timestamp'})
        self.assertEqual(resultset['count'], 3)
        self.assertEqual(resultset['results'][0]['id'], 3)
        self.assertEqual(resultset['results'][1]['id'], 2)
        self.assertEqual(resultset['results'][2]['id'], 1)

        # Search
        resultset = self._request('dsmrreading', data={'timestamp__gte': '2016-07-01 21:00:00'})  # Z+02:00
        self.assertEqual(resultset['count'], 2)
        self.assertEqual(resultset['results'][0]['id'], 2)
        self.assertEqual(resultset['results'][1]['id'], 3)

        resultset = self._request('dsmrreading', data={'timestamp__lte': '2016-07-01 21:00:00'})  # Z+02:00
        self.assertEqual(resultset['count'], 2)
        self.assertEqual(resultset['results'][0]['id'], 1)
        self.assertEqual(resultset['results'][1]['id'], 2)

    def test_post(self):
        TELEGRAM = {
            'electricity_currently_delivered': 1.500,
            'electricity_currently_returned': 0.025,
            'electricity_delivered_1': 2000,
            'electricity_delivered_2': 3000,
            'electricity_returned_1': 0,
            'electricity_returned_2': 0,
            'timestamp': '2017-01-01T00:00:00+01:00',
        }
        self.assertEqual(DsmrReading.objects.all().count(), 3)

        resultset = self._request('dsmrreading', expected_code=201, method='post', data=TELEGRAM)
        self.assertEqual(float(resultset['electricity_currently_delivered']), 1.5)
        self.assertEqual(float(resultset['electricity_currently_returned']), 0.025)
        self.assertEqual(float(resultset['electricity_delivered_1']), 2000)
        self.assertEqual(float(resultset['electricity_delivered_2']), 3000)
        self.assertEqual(float(resultset['electricity_returned_1']), 0)
        self.assertEqual(float(resultset['electricity_returned_2']), 0)
        self.assertEqual(resultset['timestamp'], '2017-01-01T00:00:00+01:00')
        self.assertIsNone(resultset['phase_currently_delivered_l1'])
        self.assertIsNone(resultset['phase_currently_delivered_l2'])
        self.assertIsNone(resultset['phase_currently_delivered_l3'])
        self.assertIsNone(resultset['extra_device_timestamp'])
        self.assertIsNone(resultset['extra_device_delivered'])
        self.assertEqual(DsmrReading.objects.all().count(), 4)

        # Again, with UTC.
        TELEGRAM['timestamp'] = '2017-01-01T00:00:00Z'
        resultset = self._request('dsmrreading', expected_code=201, method='post', data=TELEGRAM)
        self.assertEqual(resultset['timestamp'], '2017-01-01T01:00:00+01:00')
        self.assertEqual(DsmrReading.objects.all().count(), 5)

        # Now with optional data.
        TELEGRAM['timestamp'] = '2017-01-02T00:00:00Z'
        TELEGRAM['extra_device_timestamp'] = '2017-01-02T01:00:00Z'
        TELEGRAM['extra_device_delivered'] = 1234
        TELEGRAM['phase_currently_delivered_l1'] = 0.5
        TELEGRAM['phase_currently_delivered_l2'] = 0.75
        TELEGRAM['phase_currently_delivered_l3'] = 0.25
        resultset = self._request('dsmrreading', expected_code=201, method='post', data=TELEGRAM)
        self.assertEqual(resultset['timestamp'], '2017-01-02T01:00:00+01:00')
        self.assertEqual(resultset['extra_device_timestamp'], '2017-01-02T02:00:00+01:00')
        self.assertEqual(float(resultset['extra_device_delivered']), 1234)
        self.assertEqual(float(resultset['phase_currently_delivered_l1']), 0.5)
        self.assertEqual(float(resultset['phase_currently_delivered_l2']), 0.75)
        self.assertEqual(float(resultset['phase_currently_delivered_l3']), 0.25)
        self.assertEqual(DsmrReading.objects.all().count(), 6)
