from django.db.migrations.executor import MigrationExecutor
from django.urls.base import reverse
from django.db import connection
from django.apps import apps

from dsmr_api.models import APISettings
from dsmr_api.tests.v2 import APIv2TestCase


class APIv2TestCase(APIv2TestCase):
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

    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    def test_user_does_not_exist(self):
        """ Tests what happens when the API user was not created. """
        # Roll back migration creating the API user.
        MigrationExecutor(connection=connection).migrate([(self.app, '0002_generate_random_auth_key')])

        response = self.client.get(
            reverse('{}:dsmrreading'.format(self.NAMESPACE)),
            HTTP_X_AUTHKEY=self.api_settings.auth_key,
        )
        self.assertEqual(response.status_code, 500)
