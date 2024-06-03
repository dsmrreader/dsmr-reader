from django.test import TestCase
from django.conf import settings

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin


class TestBackendInfra(InterceptCommandStdoutMixin, TestCase):
    def test_supported_vendors(self):
        """Check whether supported vendors is as expected."""
        self.assertEqual(
            settings.DSMRREADER_SUPPORTED_DB_VENDORS, ("postgresql", "mysql")
        )

    def test_timezone(self):
        """Verify timezone setting, as it should never be altered."""
        self.assertEqual(settings.TIME_ZONE, "Europe/Amsterdam")

    def test_version(self):
        """Verify version setting."""
        self.assertIsNotNone(settings.DSMRREADER_VERSION)

    def test_pending_migrations(self):
        """Tests whether there are any model changes, which are not reflected in migrations."""
        self.assertEqual(
            self._intercept_command_stdout("makemigrations", dry_run=True),
            "No changes detected\n",
            'Please run "./manage.py makemigrations"!',
        )

    def test_internal_check(self):
        """Tests whether Django passes its internal 'check' command."""
        self.assertEqual(
            self._intercept_command_stdout("check"),
            "System check identified no issues (0 silenced).\n",
        )
