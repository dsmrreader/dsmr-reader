from django.db import connection
from django.test import TestCase

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin


class TestCommand(InterceptCommandStdoutMixin, TestCase):
    def test_dsmr_debuginfo(self):
        if connection.vendor != 'postgres':  # pragma: no cover
            return self.skipTest(reason='Only PostgreSQL supported')

        # Just test whether it exists and runs.
        self._intercept_command_stdout('dsmr_debuginfo')
