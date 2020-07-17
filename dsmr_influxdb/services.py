from decimal import Decimal
import configparser
import logging
import json

from django.conf import settings
from django.db.transaction import atomic
from influxdb import InfluxDBClient

from dsmr_influxdb.models import InfluxdbIntegrationSettings, InfluxdbMeasurement

logger = logging.getLogger('commands')


def initialize_client():
    influxdb_settings = InfluxdbIntegrationSettings.get_solo()

    if not influxdb_settings.enabled:
        return logger.debug('INFLUXDB: Integration disabled in settings')

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
    logger.debug('INFLUXDB: Initialized client')

    # Always make sure the database exists.
    logger.debug('INFLUXDB: Creating InfluxDB database "%s"', influxdb_settings.database)
    influxdb_client.create_database(influxdb_settings.database)

    return influxdb_client


@atomic  # ACID!
def run(influxdb_client):
    """ Processes queued measurements. """
    # Keep batches small, only send the latest X items stored. The rest will be purged (in case of delay).
    selection = InfluxdbMeasurement.objects.all().order_by('-pk')[0:settings.DSMRREADER_INFLUXDB_MAX_MESSAGES_IN_QUEUE]

    if not selection:
        return

    logger.info('INFLUXDB: Processing %d measurement(s)', len(selection))
    points = []

    for current in selection:
        points.append({
            "measurement": current.measurement_name,
            "time": current.time,
            "fields": json.loads(current.fields),
        })

    influxdb_client.write_points(points)
    InfluxdbMeasurement.objects.all().delete()  # This purges the remainder as well.


def publish_dsmr_reading(instance):
    influxdb_settings = InfluxdbIntegrationSettings.get_solo()

    # Integration disabled.
    if not influxdb_settings.enabled:
        return

    config_parser = configparser.ConfigParser()
    config_parser.read_string(influxdb_settings.formatting)
    data_source = instance.__dict__
    for current_measurement in config_parser.sections():
        measurement_fields = {}

        for instance_field_name in config_parser[current_measurement]:
            influxdb_field_name = config_parser[current_measurement][instance_field_name]
            measurement_fields[influxdb_field_name] = data_source[instance_field_name]

        InfluxdbMeasurement.objects.create(
            measurement_name=current_measurement,
            time=data_source['timestamp'],
            fields=json.dumps(
                measurement_fields,
                default=serialize_decimal_to_float
            )
        )


def serialize_decimal_to_float(obj):
    """ Workaround to make sure Decimals are not converted to strings here. """
    if isinstance(obj, Decimal):
        return float(obj)

    raise TypeError(type(obj).__name__)
