from django.test import TestCase
from django.test.client import Client
from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

from dsmr_stats.models.note import Note


class TestNote(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser('testuser', 'unknown@localhost', 'passwd')
        self.instance = Note.objects.create(day=timezone.now(), description='Test')

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(Note))

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'Note')

    def test_admin_day_parameter(self):
        """ The admin form supports a parameter for setting the initial day used. """
        view_url = reverse('admin:dsmr_stats_note_add')
        self.client.login(username='testuser', password='passwd')

        # Test both without and with day parameter.
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.get('{}?day=01-01-2016'.format(view_url))
        self.assertEqual(response.status_code, 200)
