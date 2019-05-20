from unittest import mock

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls.base import reverse
from django.utils import timezone

from dsmr_backend.models.schedule import ScheduledProcess


class TestAdmin(TestCase):
    """ Test whether views render at all. """
    VIEWS = (
        'admin:dsmr_backend_scheduledprocess_changelist',
        'admin:dsmr_backend_emailsettings_changelist',
        'admin:dsmr_backend_scheduledprocess_changelist',
    )

    def setUp(self):
        username = 'testuser'
        password = 'passwd'
        User.objects.create_superuser(username, 'unknown@localhost', password)

        self.client = Client()
        self.client.login(username=username, password=password)

    def test_admin(self):
        for current in self.VIEWS:
            response = self.client.get(reverse(current))
            self.assertEqual(response.status_code, 200)

    def test_scheduledprocess(self):
        ScheduledProcess.objects.all().delete()
        dummy = ScheduledProcess.objects.create(
            name='Fake',
            module='non.existing',
        )

        # Test future planned.
        dummy.planned = timezone.now() + timezone.timedelta(hours=1)
        dummy.save()

        for current in self.VIEWS:
            response = self.client.get(reverse(current))
            self.assertEqual(response.status_code, 200)

    @mock.patch('dsmr_backend.services.email.send')
    def test_send_test_email(self, service_mock):
        REVERSE = 'admin:dsmr_backend_emailsettings_changelist'
        # Default.
        response = self.client.post(reverse(REVERSE))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(service_mock.called)

        # OK.
        service_mock.reset_mock()
        response = self.client.post(
            reverse(REVERSE),
            data=dict(send_test_email='yes')
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(service_mock.called)

        # Failed.
        service_mock.reset_mock()
        service_mock.side_effect = Exception("Chaos monkey")
        response = self.client.post(
            reverse(REVERSE),
            data=dict(send_test_email='yes')
        )
        self.assertEqual(response.status_code, 302)
