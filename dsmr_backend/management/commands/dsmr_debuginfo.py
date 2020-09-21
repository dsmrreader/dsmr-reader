from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection

from dsmr_backend.models.settings import BackendSettings
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import RetentionSettings, DataloggerSettings
from dsmr_datalogger.models.statistics import MeterStatistics


class Command(BaseCommand):  # pragma: nocover
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
        self._dump_meter_info()
        self._dump_data_info()
        self._dump_pg_size()

        if options['with_indices']:
            self._dump_pg_indices()

        self._print_end()

    def _dump_meter_info(self):
        self._print_header('Smart meter')
        self._pretty_print('Telegram version (latest reading)', 'v{}'.format(MeterStatistics.get_solo().dsmr_version))
        self._pretty_print('Setting: Telegram parser', DataloggerSettings.get_solo().dsmr_version)

    def _dump_application_info(self):
        self._print_header('DSMR-reader')
        self._pretty_print('Version', 'v{}'.format(settings.DSMRREADER_VERSION))
        self._pretty_print('Database engine/vendor', connection.vendor)
        self._pretty_print('Setting: Backend process sleep', '{} s'.format(BackendSettings.get_solo().process_sleep))
        self._pretty_print('Setting: Datalogger process sleep', '{} s'.format(DataloggerSettings.get_solo().process_sleep))
        self._pretty_print('Setting: Retention cleans up after', '{} h'.format(
            RetentionSettings.get_solo().data_retention_in_hours
        ))

    def _dump_data_info(self):
        self._print_header('Data')
        self._pretty_print('Stored: Telegram records total', DsmrReading.objects.count())
        self._pretty_print('                      \\_ unprocessed', DsmrReading.objects.unprocessed().count())
        self._pretty_print('Stored: Electricity consumption records', ElectricityConsumption.objects.count())
        self._pretty_print('Stored: Gas consumption records', GasConsumption.objects.count())

    def _dump_pg_size(self):
        if connection.vendor != 'postgresql':
            return

        # @see https://wiki.postgresql.org/wiki/Disk_Usage
        MIN_SIZE_B = 1 * 1024 * 1024
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
            cursor.execute(size_sql, [MIN_SIZE_B])
            self._print_header('PostgreSQL size of largest tables (> 1MB)')

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
            self._print_header('PostgreSQL indices of largest tables')

            for tablename, indexname in cursor.fetchall():
                self._pretty_print(tablename, indexname)

    def _print_start(self):
        print()
        print('<--- COPY OUTPUT AFTER THIS LINE --->')
        print()
        print()
        print('```')

    def _pretty_print(self, what, value):
        print('  {:55}{:>10}'.format(what, value))

    def _print_header(self, what):
        print()
        print(what.upper())

    def _print_end(self):
        print()
        print('```')
        print()
        print('<--- COPY OUTPUT UNTIL THIS LINE --->')
        print()
