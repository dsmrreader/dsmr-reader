import pprint
import urllib
import json

import requests
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dsmr_api.models import APISettings


class Command(BaseCommand):
    help = 'Testscript for testing the v2 API.'
    API_KEY = None

    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError('Only meant for development environment!')

        self.API_KEY = APISettings.get_solo().auth_key

        self._test_dsmrreading()
        self._test_electricity_consumption()
        self._test_gas_consumption()
        self._test_day_statistics()
        self._test_hour_statistics()

    def _test_dsmrreading(self):
        URI = 'datalogger/dsmrreading'
        self._request(uri=URI, limit=2, ordering='-timestamp', timestamp__gte='2017-04-11 05:59:00')
#         self._request(method='post', uri=URI, **{
#             'electricity_currently_delivered': 1.500,
#             'electricity_currently_returned': 0.025,
#             'electricity_delivered_1': 2000,
#             'electricity_delivered_2': 3000,
#             'electricity_returned_1': 0,
#             'electricity_returned_2': 0,
#             'timestamp': '2017-04-15T00:00:00+02',
#         })

    def _test_electricity_consumption(self):
        URI = 'consumption/electricity'
        self._request(uri=URI, limit=5, ordering='-read_at', read_at__lte='2017-04-10 03:00:00')

    def _test_gas_consumption(self):
        URI = 'consumption/gas'
        self._request(uri=URI, limit=5, ordering='-read_at', read_at__gte='2017-04-10 03:00:00')

    def _test_day_statistics(self):
        URI = 'statistics/day'
        self._request(uri=URI, day='2017-01-01')
        self._request(uri=URI, ordering='-day', day__gte='2016-01-01', day__lte='2016-02-01')

    def _test_hour_statistics(self):
        URI = 'statistics/hour'
        self._request(uri=URI, limit=3, hour_start__gte='2016-01-01 12:00:00')

    def _request(self, uri, method='get', **data):
        if method == 'get':
            uri = '{}?{}'.format(uri, urllib.parse.urlencode(data))
            data = None

        print(' {} /api/v2/{}'.format(method.upper(), uri))
        response = getattr(requests, method)(
            'http://localhost:8000/api/v2/{}'.format(uri),
            headers={'X-AUTHKEY': self.API_KEY},
            data=data,
        )
        print(response)

        pprint.pprint(json.loads(response.text), indent=4)
