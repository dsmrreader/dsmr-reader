from unittest import mock

from django.test.testcases import TestCase
from django.test.client import Client
from django.urls import reverse

from dsmr_api.models import APISettings
from dsmr_datalogger.models.reading import DsmrReading


class TestAPIv1(TestCase):
    """ Test whether views render at all. """
    namespace = 'api-v1'

    def setUp(self):
        self.client = Client()
        self._api_settings = APISettings.get_solo()
        self._api_settings.allow = True
        self._api_settings.save()

        # Since we're only having one call anyway.
        self._api_url = reverse('{}:datalogger-dsmrreading'.format(self.namespace))
        self.assertEqual(self._api_url, '/api/v1/datalogger/dsmrreading')

        self._telegram = ''.join([
            "/KFM5KAIFA-METER\r\n",
            "\r\n",
            "1-3:0.2.8(42)\r\n",
            "0-0:1.0.0(160303164347W)\r\n",
            "0-0:96.1.1(*******************************)\r\n",
            "1-0:1.8.1(001073.079*kWh)\r\n",
            "1-0:1.8.2(001263.199*kWh)\r\n",
            "1-0:2.8.1(000000.000*kWh)\r\n",
            "1-0:2.8.2(000000.000*kWh)\r\n",
            "0-0:96.14.0(0002)\r\n",
            "1-0:1.7.0(00.143*kW)\r\n",
            "1-0:2.7.0(00.000*kW)\r\n",
            "0-0:96.7.21(00006)\r\n",
            "0-0:96.7.9(00003)\r\n",
            "1-0:99.97.0(1)(0-0:96.7.19)(000101000001W)(2147483647*s)\r\n",
            "1-0:32.32.0(00000)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:21.7.0(00.143*kW)\r\n",
            "1-0:22.7.0(00.000*kW)\r\n",
            "!74B0\n",
        ])

    def test_invalid_method(self):
        """ Currently only a single call using POST is allowed. """
        response = self.client.get(self._api_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'')

    def test_allow(self):
        """ API should be disabled by default. """
        self._api_settings.allow = False
        self._api_settings.save()
        self.assertFalse(self._api_settings.allow)

        response = self.client.post(self._api_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b'API is disabled')

        self._api_settings.allow = True
        self._api_settings.save()

        response = self.client.post(self._api_url)
        self.assertNotEqual(response.status_code, 405)

    def test_auth_key(self):
        response = self.client.post(self._api_url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b'Invalid auth key')

        response = self.client.post(self._api_url, HTTP_X_AUTHKEY=self._api_settings.auth_key)
        self.assertNotEqual(response.status_code, 403)

    def test_data_validation(self):
        """ Shallow data verification. """
        response = self.client.post(self._api_url, HTTP_X_AUTHKEY=self._api_settings.auth_key)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, b'Invalid data')

        response = self.client.post(
            self._api_url,
            data={'telegram': 'fake-but-present'},
            HTTP_X_AUTHKEY=self._api_settings.auth_key
        )
        self.assertNotEqual(response.status_code, 400)

    def test_parse_telegram(self):
        """ Actual insert of telegram/reading. """
        response = self.client.post(
            self._api_url,
            data={'telegram': 'blablabla'},
            HTTP_X_AUTHKEY=self._api_settings.auth_key
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.content, b'Failed to parse telegram')

    @mock.patch('dsmr_datalogger.services.verify_telegram_checksum')
    def test_okay(self, verify_telegram_checksum_mock):
        self.assertFalse(DsmrReading.objects.exists())

        response = self.client.post(
            self._api_url,
            data={'telegram': self._telegram},
            HTTP_X_AUTHKEY=self._api_settings.auth_key
        )

        # Disable CRC for this test, as it's tested elsewhere. But verify that it was called anyway.
        self.assertTrue(verify_telegram_checksum_mock.called)
        self.assertTrue(DsmrReading.objects.exists())
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content, b'')
