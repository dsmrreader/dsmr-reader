from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.management import CommandError
from django.test import override_settings
from django.test.testcases import TestCase

from dsmr_backend.tests.mixins import InterceptStdoutMixin


class TestCommands(InterceptStdoutMixin, TestCase):
    @override_settings(DEBUG=True)
    def test_clear_consumption(self):
        self._intercept_command_stdout('development_reset')

    @override_settings(DEBUG=False)
    def test_fail_debug(self):
        with self.assertRaises(CommandError):
            self._intercept_command_stdout('development_reset')

    @override_settings(DEBUG=True)
    def test_update_admin_user(self):
        User.objects.create_superuser('admin', 'root@localhost', 'some-password')
        self._intercept_command_stdout('development_reset')

        self.assertIsNotNone(
            authenticate(username='admin', password='admin')  # Success
        )
