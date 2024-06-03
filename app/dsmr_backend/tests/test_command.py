from django.conf import settings
from django.db import connection
from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin


class TestCommand(InterceptCommandStdoutMixin, TestCase):
    def test_dsmr_debuginfo(self):
        if connection.vendor != "postgres":  # pragma: no cover
            return self.skipTest(reason="Only PostgreSQL supported")

        # Just test whether it exists and runs.
        self._intercept_command_stdout("dsmr_debuginfo")

    def test_check_deploy(self):
        if connection.vendor != "sqlite":  # pragma: no cover
            return self.skipTest(reason="Only SQLite supported")

        _, stderr = self._intercept_command("check", deploy=True)

        self.assertIn(settings.DSMRREADER_SYSTEM_CHECK_001, stderr)  # SQLite
        self.assertNotIn(
            settings.DSMRREADER_SYSTEM_CHECK_002, stderr
        )  # Migrations - Should be OK
