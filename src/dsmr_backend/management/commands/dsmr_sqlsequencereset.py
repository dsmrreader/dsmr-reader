from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin


class Command(InterceptCommandStdoutMixin, BaseCommand):  # pragma: nocover
    """This should prevent future issues similar to #866 and #867."""

    help = "Resets the sequences (incremental IDs) for PostgreSQL engines"

    def handle(self, **options):
        # Only applicable for PostgreSQL.
        if connection.vendor != "postgresql":
            return

        installed_apps = [x.label for x in apps.get_app_configs()]
        sql = self._intercept_command_stdout(
            "sqlsequencereset", *installed_apps, no_color=True
        )

        # Django's migrations does not have an app, so we'll just hard code it.
        sql += """
        BEGIN;
        SELECT setval(
            pg_get_serial_sequence('"django_migrations"','id'), coalesce(max("id"), 1), max("id") IS NOT null
        ) FROM "django_migrations";
        COMMIT;
        """

        with connection.cursor() as cursor:
            cursor.execute(sql)
