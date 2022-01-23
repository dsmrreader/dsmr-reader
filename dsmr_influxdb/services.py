import pickle
from collections import defaultdict
import configparser
import logging
from typing import NoReturn, Dict, Optional
import codecs

from django.conf import settings
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_influxdb.models import InfluxdbIntegrationSettings, InfluxdbMeasurement


logger = logging.getLogger('dsmrreader')


def initialize_client() -> Optional[InfluxDBClient]:
    influxdb_settings = InfluxdbIntegrationSettings.get_solo()

    if not influxdb_settings.enabled:
        return logger.debug('INFLUXDB: Integration disabled in settings (or due to an error previously)')

    use_secure_connection = influxdb_settings.secure in (
        InfluxdbIntegrationSettings.SECURE_CERT_NONE,
        InfluxdbIntegrationSettings.SECURE_CERT_REQUIRED,
    )

    if use_secure_connection:
        server_base_url = 'https://{}:{}'.format(influxdb_settings.hostname, influxdb_settings.port)
    else:
        server_base_url = 'http://{}:{}'.format(influxdb_settings.hostname, influxdb_settings.port)

    logger.debug('INFLUXDB: Initializing InfluxDB client for "%s"', server_base_url)

    influxdb_client = InfluxDBClient(
        url=server_base_url,
        token=influxdb_settings.api_token,
        verify_ssl=influxdb_settings.secure == InfluxdbIntegrationSettings.SECURE_CERT_REQUIRED,
        timeout=settings.DSMRREADER_CLIENT_TIMEOUT * 1000,  # Ms!
    )
    # logger.debug('INFLUXDB: InfluxDB client/server status: "%s"', influxdb_client.ready().status)

    if influxdb_client.buckets_api().find_bucket_by_name(influxdb_settings.bucket) is None:  # pragma: nocover
        logger.debug('INFLUXDB: Creating InfluxDB bucket "%s"', influxdb_settings.bucket)

        try:
            influxdb_client.buckets_api().create_bucket(
                bucket_name=influxdb_settings.bucket,
                org=influxdb_settings.organization
            )
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
    influxdb_settings = InfluxdbIntegrationSettings.get_solo()

    for current in selection:
        try:
            decoded_fields = codecs.decode(current.fields.encode(), 'base64')
            unpickled_fields = pickle.loads(decoded_fields)

            with influxdb_client.write_api(write_options=SYNCHRONOUS) as write_api:
                write_api.write(
                    bucket=influxdb_settings.bucket,
                    org=influxdb_settings.organization,
                    record={
                        "measurement": current.measurement_name,
                        "time": current.time,
                        "fields": unpickled_fields
                    }
                )
        except Exception as error:
            logger.error('INFLUXDB: Writing measurement(s) failed: %s, data: %s', error, current.fields)

        current.delete()

    # This purges the remainder.
    InfluxdbMeasurement.objects.all().delete()


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

        pickled_fields = pickle.dumps(measurement_fields)
        encoded_fields = codecs.encode(pickled_fields, 'base64').decode()

        InfluxdbMeasurement.objects.create(
            measurement_name=current_measurement,
            time=data_source['timestamp'],
            fields=encoded_fields
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
