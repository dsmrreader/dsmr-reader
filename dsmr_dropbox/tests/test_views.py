from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    namespace = 'dropbox'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'unknown@localhost', 'passwd')

    def test_configuration(self):
        """ Basically the same view (context vars) as the archive view. """
        view_url = reverse('{}:authorize-app'.format(self.namespace))
        # Check login required.
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], '/admin/login/?next={}'.format(view_url)
        )

        # Login and retest
        self.client.login(username='testuser', password='passwd')
        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 302, response.content)
        self.assertIn(
            'https://www.dropbox.com/oauth2/authorize?response_type=code&client_id=w5z4vlw9t2dqq5g&'
            'token_access_type=offline&code_challenge=',
            response['Location'],
        )
