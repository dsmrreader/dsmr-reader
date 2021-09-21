from collections import defaultdict
from decimal import Decimal
import configparser
import logging
import json
from typing import NoReturn, Dict

from django.conf import settings
from influxdb import InfluxDBClient

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_influxdb.models import InfluxdbIntegrationSettings, InfluxdbMeasurement


logger = logging.getLogger('dsmrreader')


def initialize_client():
    influxdb_settings = InfluxdbIntegrationSettings.get_solo()

    if not influxdb_settings.enabled:
        return logger.debug('INFLUXDB: Integration disabled in settings (or due to an error previously)')

    logger.debug(
        'INFLUXDB: Initializing InfluxDB client for "%s:%d"', influxdb_settings.hostname, influxdb_settings.port
    )
    influxdb_client = InfluxDBClient(
        host=influxdb_settings.hostname,
        port=influxdb_settings.port,
        username=influxdb_settings.username,
        password=influxdb_settings.password,
        database=influxdb_settings.database,
        ssl=influxdb_settings.secure in (
            InfluxdbIntegrationSettings.SECURE_CERT_NONE,
            InfluxdbIntegrationSettings.SECURE_CERT_REQUIRED,
        ),
        verify_ssl=influxdb_settings.secure == InfluxdbIntegrationSettings.SECURE_CERT_REQUIRED,
        timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
    )

    # Always make sure the database exists.
    logger.debug('INFLUXDB: Creating InfluxDB database "%s"', influxdb_settings.database)

    try:
        influxdb_client.create_database(influxdb_settings.database)
    except Exception as e:
        InfluxdbIntegrationSettings.objects.update(enabled=False)
        logger.error('Failed to instantiate InfluxDB connection, disabling InfluxDB integration')
        raise e

    return influxdb_client


def run(influxdb_client: InfluxDBClient) -> NoReturn:
    """ Processes queued measurements. """
    # Keep batches small, only send the latest X items stored. The rest will be purged (in case of delay).
    selection = InfluxdbMeasurement.objects.all().order_by('-pk')[
        0:settings.DSMRREADER_INFLUXDB_MAX_MEASUREMENTS_IN_QUEUE
    ]

    if not selection:
        return

    logger.info('INFLUXDB: Processing %d measurement(s)', len(selection))

    for current in selection:
        try:
            influxdb_client.write_points([
                {
                    "measurement": current.measurement_name,
                    "time": current.time,
                    "fields": json.loads(current.fields),
                }
            ])
        except Exception as error:
            logger.error('INFLUXDB: Writing measurement(s) failed: %s', error)

        current.delete()

    InfluxdbMeasurement.objects.all().delete()  # This purges the remainder.


def publish_dsmr_reading(instance: DsmrReading) -> NoReturn:
    influxdb_settings = InfluxdbIntegrationSettings.get_solo()

    # Integration disabled.
    if not influxdb_settings.enabled:
        return

    mapping = get_reading_to_measurement_mapping()
    data_source = instance.__dict__

    for current_measurement, measurement_mapping in mapping.items():
        measurement_fields = {}

        for reading_field, influxdb_field in measurement_mapping.items():
            measurement_fields[influxdb_field] = data_source[reading_field]

        InfluxdbMeasurement.objects.create(
            measurement_name=current_measurement,
            time=data_source['timestamp'],
            fields=json.dumps(
                measurement_fields,
                default=serialize_decimal_to_float
            )
        )


def get_reading_to_measurement_mapping() -> Dict:
    """ Parses and returns the formatting mapping as defined by the user. """
    READING_FIELDS = [x.name for x in DsmrReading._meta.get_fields() if x.name not in ('id', 'processed')]
    mapping = defaultdict(dict)

    config_parser = configparser.ConfigParser()
    config_parser.read_string(InfluxdbIntegrationSettings.get_solo().formatting)

    for current_measurement in config_parser.sections():
        for instance_field_name in config_parser[current_measurement]:
            influxdb_field_name = config_parser[current_measurement][instance_field_name]

            if instance_field_name not in READING_FIELDS:
                logger.warning(
                    'INFLUXDB: Unknown DSMR-reading field "%s" mapped to measurement "%s"',
                    instance_field_name,
                    current_measurement
                )
                continue

            mapping[current_measurement][instance_field_name] = influxdb_field_name

    return mapping


def serialize_decimal_to_float(obj: Decimal) -> float:
    """ Workaround to make sure Decimals are not converted to strings here. """
    if not isinstance(obj, Decimal):
        raise TypeError(type(obj).__name__)

    return float(obj)
