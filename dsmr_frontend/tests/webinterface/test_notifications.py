from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from dsmr_frontend.models.message import Notification


class TestViews(TestCase):
    namespace = 'frontend'

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'unknown@localhost', 'passwd')
        Notification.objects.all().delete()  # Make sure notifications created by migrations are ignored.
        Notification.objects.create(message='TEST2')
        Notification.objects.create(message='TEST3')

    def test_notifications(self):
        view_url = reverse('{}:notifications'.format(self.namespace))

        response = self.client.get(view_url)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertIn('notifications', response.context)

    def test_xhr_notification_read(self):
        view_url = reverse('{}:notification-xhr-mark-read'.format(self.namespace))
        notification = Notification.objects.all()[0]
        self.assertFalse(notification.read)
        self.assertEqual(Notification.objects.unread().count(), 2)

        # Check login required.
        response = self.client.post(view_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], '/admin/login/?next={}'.format(view_url)
        )

        # Logged in.
        self.client.login(username='testuser', password='passwd')
        response = self.client.post(view_url, data={'notification_id': notification.pk})
        self.assertEqual(response.status_code, 200, response.content)

        # Notification should be altered now.
        self.assertEqual(Notification.objects.unread().count(), 1)
        notification.refresh_from_db()
        self.assertTrue(notification.read)

    def test_xhr_all_notifications_read(self):
        view_url = reverse('{}:notification-xhr-mark-all-read'.format(self.namespace))
        self.assertEqual(Notification.objects.unread().count(), 2)

        # Check login required.
        response = self.client.post(view_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'], '/admin/login/?next={}'.format(view_url)
        )

        # Logged in.
        self.client.login(username='testuser', password='passwd')
        response = self.client.post(view_url)
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(Notification.objects.unread().count(), 0)
