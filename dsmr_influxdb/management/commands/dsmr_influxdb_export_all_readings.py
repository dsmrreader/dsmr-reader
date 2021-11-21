import logging

from django.core.management.base import BaseCommand, CommandError
from django.core.paginator import Paginator
from django.utils import timezone
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_influxdb.models import InfluxdbIntegrationSettings
import dsmr_influxdb.services


logger = logging.getLogger('console_commands')


class Command(BaseCommand):
    help = 'Exports historic readings to the InfluxDB bucket specified as argument'

    READINGS_PER_BATCH = 100
    PK_MEASUREMENT = 'export_progress_meta'
    PK_FIELD = 'last_pk_synced'

    target_influx_bucket: str
    max_batches: int = 1
    influxdb_client: InfluxDBClient = None
    field_mapping = None

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--to-influx-bucket',
            action='store',
            dest='to_influx_bucket',
            metavar='some_influxdb_bucket',
            help='The InfluxDB bucket to export to. Always try to export to a separate test bucket first!',
            required=True
        )
        parser.add_argument(
            '--max-batches',
            action='store',
            dest='max_batches',
            metavar='COUNT',
            type=int,
            default=50,
            help='Performance related: Max number of batches to process',
        )

    def handle(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        self.target_influx_bucket = options['to_influx_bucket']
        influxdb_settings = InfluxdbIntegrationSettings.get_solo()

        # Integration disabled.
        if not influxdb_settings.enabled:
            raise CommandError('InfluxDB integration is disabled')

        self.max_batches = options['max_batches']

        if self.max_batches < 0:
            self.max_batches = 1

        logger.info('INFLUXDB EXPORT: Connecting to InfluxDB (ignore bucket name logged)')
        self.influxdb_client = dsmr_influxdb.services.initialize_client()

        logger.info(
            'INFLUXDB EXPORT: Using "%s" as export InfluxDB bucket (creating it if needed)', self.target_influx_bucket
        )

        if not self.influxdb_client.buckets_api().find_bucket_by_name(self.target_influx_bucket):
            self.influxdb_client.buckets_api().create_bucket(
                bucket_name=self.target_influx_bucket,
                org=influxdb_settings.organization
            )

        logger.info('INFLUXDB EXPORT: Fetching mapping')
        self.field_mapping = dsmr_influxdb.services.get_reading_to_measurement_mapping()

        logger.info('INFLUXDB EXPORT: Listing mapped reading fields')
        reading_fields = self.list_reading_fields()

        logger.info('INFLUXDB EXPORT: Fetching last PK synced from export_progress_meta in InfluxDB')
        last_pk = self.fetch_last_pk_synced()

        logger.info(
            'INFLUXDB EXPORT: Limiting to %d batches of max %d readings each',
            self.max_batches,
            self.READINGS_PER_BATCH
        )
        max_readings = self.max_batches * self.READINGS_PER_BATCH
        logger.info(
            'INFLUXDB EXPORT: Fetching readings with PK > %d (max number of readings %d)', last_pk, max_readings
        )
        readings = DsmrReading.objects.filter(
            pk__gt=last_pk
        ).values_list(
            *reading_fields,
            named=True
        )[0:max_readings]
        paginator = Paginator(readings, self.READINGS_PER_BATCH)

        if not paginator.count:
            return logger.info('INFLUXDB EXPORT: No (more) readings to export')

        self._export(paginator)

    def list_reading_fields(self):
        """ For performance. """
        return ['pk', 'timestamp'] + [
            f for _, y in self.field_mapping.items() for f, _ in y.items()
        ]

    def fetch_last_pk_synced(self):
        """ Continue progress where left off. """
        influxdb_settings = InfluxdbIntegrationSettings.get_solo()
        results = self.influxdb_client.query_api().query(
            'from(bucket:"{bucket}")'
            '  |> range(start: -1h)'
            '  |> sort(columns: ["{field}", "_value"], desc: true)'
            '  |> limit(n: 1)'.format(
                bucket=self.target_influx_bucket,
                field=self.PK_FIELD,
            ),
            org=influxdb_settings.organization
        )

        if not results or not results[0] or not results[0].records[0]:
            return 0

        result = results[0].records[0]
        last_pk = result.get_value()
        logger.info(
            'INFLUXDB EXPORT: Last PK synced %d @ %s (export_progress_meta in InfluxDB)',
            last_pk,
            result.get_time()
        )

        return last_pk

    def fetch_readings(self, reading_fields):
        return

    def _export(self, paginator):
        for page_num in paginator.page_range:
            batch = iter(paginator.get_page(page_num))
            logger.info(
                'INFLUXDB EXPORT: Processing batch (limit: %d): %d of %d',
                self.max_batches,
                page_num,
                paginator.num_pages,
            )
            self._export_batch(batch)

    def _export_batch(self, batch):
        influxdb_settings = InfluxdbIntegrationSettings.get_solo()

        for current_reading in batch:
            last_pk = current_reading.pk

            for current_measurement, measurement_mapping in self.field_mapping.items():
                measurement_fields = {}

                for reading_field, influxdb_field in measurement_mapping.items():
                    value = getattr(current_reading, reading_field)

                    if value is None:
                        continue

                    measurement_fields[influxdb_field] = getattr(current_reading, reading_field)

                if not measurement_fields:
                    continue

                with self.influxdb_client.write_api(write_options=SYNCHRONOUS) as write_api:
                    try:
                        write_api.write(
                            bucket=self.target_influx_bucket,
                            org=influxdb_settings.organization,
                            record={
                                "measurement": current_measurement,
                                "time": current_reading.timestamp,
                                "fields": measurement_fields,
                            }
                        )
                    except Exception as error:
                        logger.error('INFLUXDB EXPORT: Writing measurement(s) failed: %s', error)
                        raise

                    write_api.write(
                        bucket=self.target_influx_bucket,
                        org=influxdb_settings.organization,
                        record={
                            "measurement": self.PK_MEASUREMENT,
                            "time": timezone.now(),
                            "fields": {
                                self.PK_FIELD: last_pk
                            },
                        }
                    )
