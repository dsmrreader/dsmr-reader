from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls.base import reverse
from django.utils import timezone

from dsmr_backend.models import ScheduledCall


class TestAdmin(TestCase):
    """ Test whether views render at all. """
    VIEWS = (
        'admin:dsmr_backend_scheduledcall_changelist',
        # '/admin/dsmr_backend/scheduledcall/'
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

    def test_admin_future(self):
        ScheduledCall.objects.all().delete()
        dummy = ScheduledCall.objects.create(
            name='Fake',
            module_path='non.existing',
        )
        dummy.next_call = timezone.now() + timezone.timedelta(hours=1)
        dummy.save()

        for current in self.VIEWS:
            response = self.client.get(reverse(current))
            self.assertEqual(response.status_code, 200)
