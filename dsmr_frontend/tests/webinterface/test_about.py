from unittest import mock
import json

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class TestAbout(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unauthenticated(self):
        response = self.client.get(
            reverse('frontend:about')
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn('monitoring_issues', response.context)


class TestAboutXhrUpdateCheck(TestCase):
    def setUp(self):
        self.client = Client()

    def test_unauthenticated(self):
        response = self.client.get(
            reverse('frontend:about-xhr-update-check')
        )
        self.assertEqual(response.status_code, 200, response.content)


class TestAboutXhrDebugInfo(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'unknown@localhost', 'passwd')

    def test_unauthenticated(self):
        view_url = reverse('frontend:about-xhr-debug-info')
        response = self.client.get(view_url)

        self.assertEqual(response.status_code, 302, response.content)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], '/admin/login/?next={}'.format(view_url)
        )

    @mock.patch('dsmr_frontend.views.about.AboutXhrDebugInfo._intercept_command_stdout')
    def test_authenticated(self, dump_mock):
        dump_mock.return_value = 'some fake dump'

        self.client.login(username='testuser', password='passwd')

        response = self.client.get(
            reverse('frontend:about-xhr-debug-info')
        )
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(json.loads(response.content), {'dump': 'some fake dump'})
