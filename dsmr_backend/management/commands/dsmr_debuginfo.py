import platform

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import RetentionSettings, DataloggerSettings
from dsmr_datalogger.models.statistics import MeterStatistics


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
        self._dump_os_info()
        self._dump_application_info()
        self._dump_data_info()
        self._dump_pg_size()

        if options['with_indices']:
            self._dump_pg_indices()

        self._print_end()

    def _dump_os_info(self):
        self._print_header('OS')
        self._pretty_print_short('Python version', 'v{}'.format(platform.python_version()))
        self._pretty_print_short('Platform', '{} ({})'.format(platform.system(), platform.processor()))
        self._pretty_print_short('System', '{}'.format(platform.platform()))

    def _dump_application_info(self):
        pending_migrations = []

        for line in self._intercept_command_stdout('showmigrations', no_color=True).split("\n"):
            if line.startswith(' [ ]'):
                pending_migrations.append(line)

        pending_migrations_count = len(pending_migrations)

        self._print_header('DSMR-reader')
        self._pretty_print('Version', 'v{}'.format(settings.DSMRREADER_VERSION))
        self._pretty_print('Backend sleep', '{} s'.format(BackendSettings.get_solo().process_sleep))
        self._pretty_print('Datalogger sleep', '{} s'.format(DataloggerSettings.get_solo().process_sleep))
        self._pretty_print('Retention cleans up after', '{} h'.format(
            RetentionSettings.get_solo().data_retention_in_hours or '-'
        ))
        self._pretty_print('Telegram parser', DataloggerSettings.get_solo().dsmr_version)
        self._pretty_print('Database engine/vendor', connection.vendor)

        if pending_migrations_count > 0:
            self._pretty_print('(!) Database migrations pending', '{} (!)'.format(pending_migrations_count))

    def _dump_data_info(self):
        self._print_header('Data')
        self._pretty_print('Telegrams', '')
        self._pretty_print('  - total', DsmrReading.objects.count() or '-')
        self._pretty_print('  - unprocessed', DsmrReading.objects.unprocessed().count() or '-')
        self._pretty_print('  - version (latest reading)', '"{}"'.format(MeterStatistics.get_solo().dsmr_version))
        self._pretty_print('Consumption records', '')
        self._pretty_print('  - electricity', ElectricityConsumption.objects.count() or '-')
        self._pretty_print('  - gas', GasConsumption.objects.count() or '-')

    def _dump_pg_size(self):
        if connection.vendor != 'postgresql':
            return

        # @see https://wiki.postgresql.org/wiki/Disk_Usage
        MIN_SIZE_MB = 5
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
            self._print_header('PostgreSQL size of largest tables (> {} MB)'.format(MIN_SIZE_MB))

            for table, size in cursor.fetchall():
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

    def _print_start(self):
        print()
        print('<--- COPY OUTPUT AFTER THIS LINE --->')
        print()
        print()
        print('```')

    def _pretty_print(self, what, value):
        print('    {:70}{:>20}'.format(what, value))

    def _pretty_print_short(self, what, value):
        print('    {:20}{:>70}'.format(what, value))

    def _print_header(self, what):
        print()
        print(what.upper())

    def _print_end(self):
        print()
        print('```')
        print()
        print('<--- COPY OUTPUT UNTIL THIS LINE --->')
        print()
