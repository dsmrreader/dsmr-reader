import json

from django.conf import settings
from django.db.transaction import atomic
from influxdb import InfluxDBClient

from dsmr_influxdb.models import InfluxdbIntegrationSettings, InfluxdbMeasurement


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
        timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
    )

    # Always make sure the database exists.
    influxdb_client.create_database(influxdb_settings.database)

    return influxdb_client


@atomic
def run(influxdb_client):
    """
    Processes queued measurements. Submits them in bulk, but does not garantuee the prevention of any leftovers.

    WARNING: This block is atomic.
    Submitting the measurements should either fail or succeed, including its deletion.
    """
    remaining = InfluxdbMeasurement.objects.all()[0:50]

    if not remaining.count():
        return

    points = []

    for current in remaining:
        points.append({
            "measurement": current.measurement_name,
            "time": current.time,
            "fields": json.loads(current.fields)
        })

    influxdb_client.write_points(points)
    remaining.delete()
