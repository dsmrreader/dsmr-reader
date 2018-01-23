from django.db.migrations.executor import MigrationExecutor
from django.db.migrations.recorder import MigrationRecorder
from django.urls import reverse
from django.test import TestCase, Client
from django.db import connection
from django.apps import apps

from dsmr_frontend.models.message import Notification


class TestRegression(TestCase):
    """
    Regression for: NoReverseMatch at / Reverse for 'docs' #175.
    Thanks to: https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    """

    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    def setUp(self):
        self.client = Client()

    def test_no_reverse_match_docs(self):
        """ Test whether the docs URL in old notfications are converted to their new location. """
        Notification.objects.create(
            message='Fake',
            redirect_to='frontend:docs',  # Non-existing legacy.
        )

        # This SHOULD crash.
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 500)

        # Now we fake applying the migration (again for this test).
        MigrationRecorder.Migration.objects.filter(app='dsmr_frontend', name='0009_docs_no_reverse_match').delete()
        MigrationExecutor(connection=connection).migrate([(self.app, '0009_docs_no_reverse_match')])

        # The error should be fixed now.
        response = self.client.get(reverse('frontend:dashboard'))
        self.assertEqual(response.status_code, 200)
