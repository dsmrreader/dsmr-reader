from django.contrib.auth.models import User
from django.urls.base import reverse
from django.apps import apps

from dsmr_api.models import APISettings
from dsmr_api.tests.v2 import APIv2TestCase


class TestGeneric(APIv2TestCase):
    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    def test_disabled(self):
        """ Test API should be disabled. """
        APISettings.objects.all().update(allow=False)

        response = self.client.get(reverse('{}:dsmrreading'.format(self.NAMESPACE)))
        self.assertEqual(response.status_code, 403)

    def test_anonymous(self):
        """ Test API key is required. """
        response = self.client.get(reverse('{}:dsmrreading'.format(self.NAMESPACE)))
        self.assertEqual(response.status_code, 403)

    def test_invalid_key(self):
        """ Test API key is validated. """
        response = self.client.get(
            reverse('{}:dsmrreading'.format(self.NAMESPACE)),
            HTTP_X_AUTHKEY='INVALID-KEY'
        )
        self.assertEqual(response.status_code, 403)

    def test_user_does_not_exist(self):
        """ Tests what happens when the API user was not created. """
        User.objects.all().delete()

        response = self.client.get(
            reverse('{}:dsmrreading'.format(self.NAMESPACE)),
            HTTP_X_AUTHKEY=self.api_settings.auth_key,
        )
        self.assertEqual(response.status_code, 500)

    def test_x_auth_header(self):
        """ Tests primary auth header (X-AUTHKEY: <key>). """
        response = self.client.get(
            reverse('{}:dsmrreading'.format(self.NAMESPACE)),
            HTTP_X_AUTHKEY=self.api_settings.auth_key
        )
        self.assertEqual(response.status_code, 200)

    def test_authorization_header(self):
        """ Tests secondary auth header (AUTHORIZATION: Token <key>). """
        response = self.client.get(
            reverse('{}:dsmrreading'.format(self.NAMESPACE)),
            HTTP_AUTHORIZATION='Token {}'.format(self.api_settings.auth_key)
        )
        self.assertEqual(response.status_code, 200)
