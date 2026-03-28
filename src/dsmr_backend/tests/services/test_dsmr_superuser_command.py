import os
from unittest import mock

from django.contrib.auth.models import User
from django.core.management import CommandError
from django.test import RequestFactory, TestCase

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin


class TestDsmrSuperuserCommand(InterceptCommandStdoutMixin, TestCase):
    def _authenticate(self, username: str, password: str) -> bool:
        from django.contrib.auth import authenticate

        request = RequestFactory().get("/")
        return authenticate(request=request, username=username, password=password) is not None

    def test_missing_username_raises(self):
        with mock.patch.dict(
            os.environ, {"DSMRREADER_ADMIN_USER": "", "DSMRREADER_ADMIN_PASSWORD": "secret"}  # noqa: S105
        ):
            with self.assertRaises(CommandError):
                self._intercept_command_stdout("dsmr_superuser")

    def test_missing_password_raises(self):
        with mock.patch.dict(
            os.environ, {"DSMRREADER_ADMIN_USER": "admin", "DSMRREADER_ADMIN_PASSWORD": ""}  # noqa: S105
        ):
            with self.assertRaises(CommandError):
                self._intercept_command_stdout("dsmr_superuser")

    def test_creates_new_superuser(self):
        self.assertFalse(User.objects.filter(username="admin").exists())

        with mock.patch.dict(
            os.environ, {"DSMRREADER_ADMIN_USER": "admin", "DSMRREADER_ADMIN_PASSWORD": "secret"}  # noqa: S105
        ):
            self._intercept_command_stdout("dsmr_superuser")

        user = User.objects.get(username="admin")
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertTrue(self._authenticate("admin", "secret"))  # noqa: S106

    def test_updates_existing_superuser_password(self):
        User.objects.create_superuser("admin", "admin@localhost", "old-secret")

        with mock.patch.dict(
            os.environ, {"DSMRREADER_ADMIN_USER": "admin", "DSMRREADER_ADMIN_PASSWORD": "new-secret"}  # noqa: S105
        ):
            self._intercept_command_stdout("dsmr_superuser")

        self.assertFalse(self._authenticate("admin", "old-secret"))  # noqa: S106
        self.assertTrue(self._authenticate("admin", "new-secret"))  # noqa: S106

    def test_reactivates_inactive_superuser(self):
        user = User.objects.create_superuser("admin", "admin@localhost", "secret")
        user.is_active = False
        user.save()

        with mock.patch.dict(
            os.environ, {"DSMRREADER_ADMIN_USER": "admin", "DSMRREADER_ADMIN_PASSWORD": "secret"}  # noqa: S105
        ):
            self._intercept_command_stdout("dsmr_superuser")

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_deactivates_other_superusers(self):
        User.objects.create_superuser("other", "other@localhost", "other-secret")

        with mock.patch.dict(
            os.environ, {"DSMRREADER_ADMIN_USER": "admin", "DSMRREADER_ADMIN_PASSWORD": "secret"}  # noqa: S105
        ):
            self._intercept_command_stdout("dsmr_superuser")

        self.assertFalse(User.objects.get(username="other").is_active)
        self.assertTrue(User.objects.get(username="admin").is_active)
