import os

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
        User.objects.create_superuser('admin', 'root@localhost', 'admin')
        self._intercept_command_stdout('development_reset')

    def test_dsmr_superuser_no_env_vars(self):
        """ Command should crash without env vars. """
        if os.environ.get('CIRCLECI'):  # noqa
            self.skipTest('Skipping test on CircleCI (test import issue)')

        User.objects.all().delete()

        from test.support import EnvironmentVarGuard
        temp_env = EnvironmentVarGuard()

        with temp_env:
            with self.assertRaises(CommandError):
                self._intercept_command_stdout('dsmr_superuser')

            temp_env.set('DSMR_USER', 'testuser')

            with self.assertRaises(CommandError):
                self._intercept_command_stdout('dsmr_superuser')

            temp_env.set('DSMR_PASSWORD', 'testpass')

            self._intercept_command_stdout('dsmr_superuser')

    def test_dsmr_superuser_initial(self):
        """ New superuser should be created. """
        if os.environ.get('CIRCLECI'):  # noqa
            self.skipTest('Skipping test on CircleCI (test import issue)')

        my_username = 'testuser'
        my_password = 'testpass'
        self.assertFalse(User.objects.filter(username=my_username, is_superuser=True).exists())

        from test.support import EnvironmentVarGuard
        temp_env = EnvironmentVarGuard()
        temp_env.set('DSMR_USER', my_username)
        temp_env.set('DSMR_PASSWORD', my_password)

        with temp_env:
            self._intercept_command_stdout('dsmr_superuser')

        self.assertTrue(User.objects.filter(username=my_username, is_superuser=True).exists())

        # Actually login.
        self.assertIsNotNone(
            authenticate(username=my_username, password=my_password)
        )

    def test_dsmr_superuser_existing(self):
        """ Existing superuser password should be updated. """
        if os.environ.get('CIRCLECI'):  # noqa
            self.skipTest('Skipping test on CircleCI (test import issue)')

        my_username = 'testuser'
        old_password = 'oldpass'
        new_password = 'newpass'

        User.objects.create_superuser(my_username, 'test@localhost', old_password)

        self.assertIsNotNone(
            authenticate(username=my_username, password=old_password)  # Success
        )
        self.assertIsNone(
            authenticate(username=my_username, password=new_password)  # Fail
        )

        from test.support import EnvironmentVarGuard
        temp_env = EnvironmentVarGuard()
        temp_env.set('DSMR_USER', my_username)
        temp_env.set('DSMR_PASSWORD', new_password)

        with temp_env:
            self._intercept_command_stdout('dsmr_superuser')

        # Should be other way around now.
        self.assertIsNone(
            authenticate(username=my_username, password=old_password)  # Fail
        )
        self.assertIsNotNone(
            authenticate(username=my_username, password=new_password)  # Success
        )
