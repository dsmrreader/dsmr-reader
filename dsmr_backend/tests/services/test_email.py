from unittest import mock

from django.test import TestCase

from dsmr_backend.models.settings import EmailSettings
import dsmr_backend.services.email


class TestEmail(TestCase):
    def setUp(self):
        es = EmailSettings.get_solo()
        es.host = 'host'
        es.port = 1234
        es.username = 'username'
        es.password = 'password'
        es.use_tls = True
        es.save()

    @mock.patch('django.core.mail.EmailMessage.send')
    @mock.patch('django.core.mail.EmailMessage.attach_file')
    def test_send_email(self, attach_file_mock, send_mock):
        dsmr_backend.services.email.send(
            email_from='root@localhost',
            email_to='root@localhost',
            subject='Test',
            body='Body'
        )

        self.assertTrue(send_mock.called)
        self.assertFalse(attach_file_mock.called)

    @mock.patch('django.core.mail.EmailMessage.send')
    @mock.patch('django.core.mail.EmailMessage.attach_file')
    def test_send_email_with_attachment(self, attach_file_mock, send_mock):
        dsmr_backend.services.email.send(
            email_from='root@localhost',
            email_to='root@localhost',
            subject='Test',
            body='Body',
            attachment='/tmp/test'
        )

        self.assertTrue(send_mock.called)
        self.assertTrue(attach_file_mock.called)
