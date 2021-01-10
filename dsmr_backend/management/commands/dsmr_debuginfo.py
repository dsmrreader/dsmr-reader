import platform

from django.conf import settings
from django.contrib.humanize.templatetags import humanize
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils import timezone

from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import RetentionSettings, DataloggerSettings
from dsmr_datalogger.models.statistics import MeterStatistics
import dsmr_backend.services.backend


class Command(InterceptCommandStdoutMixin, BaseCommand):  # pragma: nocover
    help = 'Dumps debug info to share with the developer(s) when having issues'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--with-indices',
            action='store_true',
            dest='with_indices',
            default=False,
            help='Optional: Also includes important (PostgreSQL) indexes'
        )

    def handle(self, **options):
        self._print_start()
        self._dump_application_info()
        self._dump_data_info()
        self._dump_issues()
        self._dump_pg_size()

        if options['with_indices']:
            self._dump_pg_indices()

        self._print_end()

    def _dump_application_info(self):
        pending_migrations = []

        for line in self._intercept_command_stdout('showmigrations', no_color=True).split("\n"):
            if line.startswith(' [ ]'):
                pending_migrations.append(line)

        pending_migrations_count = len(pending_migrations)

        self._print_header('DSMR-reader')
        self._pretty_print('App / Python / Database', 'v{} / v{} / {}'.format(
            settings.DSMRREADER_VERSION,
            platform.python_version(),
            connection.vendor
        ))

        self._pretty_print('BE sleep / DL sleep / Retention / Override', '{}s / {}s / {}h / {}'.format(
            BackendSettings.get_solo().process_sleep,
            DataloggerSettings.get_solo().process_sleep,
            RetentionSettings.get_solo().data_retention_in_hours or '-',
            DataloggerSettings.get_solo().override_telegram_timestamp,
        ))
        self._pretty_print('Latest telegram version read / Parser settings', '"{}" / "{}"'.format(
            MeterStatistics.get_solo().dsmr_version,
            DataloggerSettings.get_solo().dsmr_version
        ))

        if pending_migrations_count > 0:
            self._pretty_print('(!) Database migrations pending', '{} (!)'.format(pending_migrations_count))

    def _dump_data_info(self):
        reading_count = self._table_record_count(DsmrReading._meta.db_table)
        electricity_count = self._table_record_count(ElectricityConsumption._meta.db_table)
        gas_count = self._table_record_count(GasConsumption._meta.db_table)

        self._print_header('Data')
        self._pretty_print('Telegrams total (est.)', reading_count or '-')
        self._pretty_print('Consumption records electricity / gas (est.)', '{} / {}'.format(
            electricity_count or '-',
            gas_count or '-'
        ))

    def _dump_issues(self):
        issues = dsmr_backend.services.backend.request_monitoring_status()

        if not issues:
            return

        self._print_header('Unresolved issues')

        for current in issues:
            self._pretty_print(
                current.description,
                humanize.naturaltime(
                    timezone.localtime(current.since)
                )
            )

    def _dump_pg_size(self):
        if connection.vendor != 'postgresql':
            return

        # @see https://wiki.postgresql.org/wiki/Disk_Usage
        MIN_SIZE_MB = 500
        size_sql = """
        SELECT nspname || '.' || relname AS "relation",
        pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
        FROM pg_class C
        LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
        WHERE nspname NOT IN ('pg_catalog', 'information_schema')
            AND C.relkind <> 'i'
            AND nspname !~ '^pg_toast'
            AND pg_total_relation_size(C.oid) > %s
        ORDER BY pg_total_relation_size(C.oid) DESC;
        """

        with connection.cursor() as cursor:
            cursor.execute(size_sql, [MIN_SIZE_MB * 1024 * 1024])
            results = cursor.fetchall()

            if not results:
                return

            self._print_header('PostgreSQL size of largest tables (> {} MB)'.format(MIN_SIZE_MB))

            for table, size in results:
                self._pretty_print(table, size)

    def _dump_pg_indices(self):
        if connection.vendor != 'postgresql':
            return

        indexes_sql = """
        SELECT tablename, indexname
        FROM pg_indexes
        WHERE schemaname = 'public'
            AND tablename IN (
                'dsmr_datalogger_dsmrreading',
                'dsmr_consumption_electricityconsumption',
                'dsmr_consumption_gasconsumption'
            )
        ORDER BY tablename, indexname;
        """

        with connection.cursor() as cursor:
            cursor.execute(indexes_sql)
            self._print_header('PostgreSQL indices of large tables')

            for tablename, indexname in cursor.fetchall():
                self._pretty_print(tablename, indexname)

    def _table_record_count(self, table_name):
        if connection.vendor != 'postgresql':
            return '??? ({})'.format(connection.vendor)

        # A live count is too slow on huge datasets, this is accurate enough:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT reltuples as approximate_row_count FROM pg_class WHERE relname = %s;',
                [table_name]
            )
            reading_count = cursor.fetchone()[0]
            return int(reading_count)

    def _print_start(self):
        self.stdout.write()
        self.stdout.write('<!-- COPY OUTPUT BELOW -->')
        self.stdout.write()
        self.stdout.write()
        self.stdout.write('```')

    def _pretty_print(self, what, value):
        self.stdout.write('    {:65}{:>40}'.format(str(what), str(value)))

    def _pretty_print_short(self, what, value):
        self.stdout.write('    {:40}{:>65}'.format(str(what), str(value)))

    def _print_header(self, what):
        self.stdout.write()
        self.stdout.write(what.upper())

    def _print_end(self):
        self.stdout.write()
        self.stdout.write('```')
        self.stdout.write()
        self.stdout.write('<!-- COPY OUTPUT ABOVE -->')
        self.stdout.write()
