import json

from django.test.client import Client
from django.test import TestCase
from django.urls.base import reverse

from dsmr_api.models import APISettings


class APIv2TestCase(TestCase):
    NAMESPACE = 'api-v2'

    client = None
    api_settings = None

    def setUp(self):
        self.client = Client()
        self.api_settings = APISettings.get_solo()
        self.api_settings.allow = True
        self.api_settings.save()

    def _request(self, view_name, method='get', expected_code=200, **kwargs):
        response = getattr(self.client, method)(
            reverse('{}:{}'.format(self.NAMESPACE, view_name)),
            HTTP_X_AUTHKEY=self.api_settings.auth_key,
            **kwargs
        )
        self.assertEqual(response.status_code, expected_code, response.content)
        result = str(response.content, 'utf-8')
        return json.loads(result)
