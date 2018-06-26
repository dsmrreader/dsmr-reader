from django.conf import settings

from dsmr_api.tests.v2 import APIv2TestCase


class TestVersion(APIv2TestCase):
    def test_get(self):
        result = self._request('application-version')

        major, minor, patch = settings.DSMRREADER_RAW_VERSION[:3]
        self.assertEqual(result['version'], '{}.{}.{}'.format(major, minor, patch))
