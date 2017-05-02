from dsmr_api.tests.v2 import APIv2TestCase


class TestDay(APIv2TestCase):
    fixtures = ['dsmr_api/test_day_statistics.json']

    def test_get(self):
        resultset = self._request('day-statistics')
        self.assertEqual(resultset['count'], 7)
        self.assertEqual(resultset['results'][0]['id'], 756)
        self.assertEqual(resultset['results'][1]['id'], 757)
        self.assertEqual(resultset['results'][5]['id'], 761)
        self.assertEqual(resultset['results'][6]['id'], 762)

        # Limit.
        resultset = self._request('day-statistics', data={'limit': 5})
        self.assertEqual(resultset['count'], 7)
        self.assertEqual(len(resultset['results']), 5)

        # Sort.
        resultset = self._request('day-statistics', data={'ordering': '-day'})
        self.assertEqual(resultset['count'], 7)
        self.assertEqual(resultset['results'][0]['id'], 762)
        self.assertEqual(resultset['results'][1]['id'], 761)
        self.assertEqual(resultset['results'][5]['id'], 757)
        self.assertEqual(resultset['results'][6]['id'], 756)

        # Search
        resultset = self._request('day-statistics', data={'day__gte': '2015-12-14'})  # Z+01:00
        self.assertEqual(resultset['count'], 4)
        self.assertEqual(resultset['results'][0]['id'], 759)
        self.assertEqual(resultset['results'][1]['id'], 760)
        self.assertEqual(resultset['results'][2]['id'], 761)
        self.assertEqual(resultset['results'][3]['id'], 762)

        resultset = self._request('day-statistics', data={'day__lte': '2015-12-14'})
        self.assertEqual(resultset['count'], 4)
        self.assertEqual(resultset['results'][0]['id'], 756)
        self.assertEqual(resultset['results'][1]['id'], 757)


class TestHour(APIv2TestCase):
    fixtures = ['dsmr_api/test_hour_statistics.json']

    def test_get(self):
        resultset = self._request('hour-statistics')
        self.assertEqual(resultset['count'], 13)
        self.assertEqual(resultset['results'][0]['id'], 14551)
        self.assertEqual(resultset['results'][1]['id'], 14552)
        self.assertEqual(resultset['results'][11]['id'], 14562)
        self.assertEqual(resultset['results'][12]['id'], 14563)

        # Limit.
        resultset = self._request('hour-statistics', data={'limit': 10})
        self.assertEqual(resultset['count'], 13)
        self.assertEqual(len(resultset['results']), 10)

        # Sort.
        resultset = self._request('hour-statistics', data={'ordering': '-hour_start'})
        self.assertEqual(resultset['count'], 13)
        self.assertEqual(resultset['results'][0]['id'], 14563)
        self.assertEqual(resultset['results'][1]['id'], 14562)
        self.assertEqual(resultset['results'][11]['id'], 14552)
        self.assertEqual(resultset['results'][12]['id'], 14551)

        # Search
        resultset = self._request('hour-statistics', data={'hour_start__gte': '2015-12-13 00:00:00'})  # Z+01:00
        self.assertEqual(resultset['count'], 11)
        self.assertEqual(resultset['results'][0]['id'], 14553)
        self.assertEqual(resultset['results'][1]['id'], 14554)
        self.assertEqual(resultset['results'][2]['id'], 14555)
        self.assertEqual(resultset['results'][3]['id'], 14556)

        resultset = self._request('hour-statistics', data={'hour_start__lte': '2015-12-13 00:00:00'})
        self.assertEqual(resultset['count'], 3)
        self.assertEqual(resultset['results'][0]['id'], 14551)
        self.assertEqual(resultset['results'][1]['id'], 14552)
