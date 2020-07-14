from decimal import Decimal

from django.utils import timezone
from influxdb import InfluxDBClient

from dsmr_influxdb.models import InfluxdbIntegrationSettings


def initialize_client():
    influxdb_settings = InfluxdbIntegrationSettings.get_solo()

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
        timeout=60,
    )

    # Always make sure the database exists.
    influxdb_client.create_database(influxdb_settings.database)

    return influxdb_client


def run(influxdb_client):
    influx_body = [
        {
            "measurement": "electricity_live",
            "time": timezone.now() - timezone.timedelta(hours=4),
            "fields": {
                "currently_delivered": Decimal('1.234'),
                "currently_returned": Decimal('0'),
            },
        }
    ]

    influxdb_client.write_points(influx_body)

    x = influxdb_client.query('select * from electricity_live')
