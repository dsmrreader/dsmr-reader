from django.core.management.base import BaseCommand

from dsmr_influxdb.models import InfluxdbMeasurement


class Command(BaseCommand):
    help = "Deletes ALL InfluxDB measurements from the queue"

    def handle(self, **options):
        InfluxdbMeasurement.objects.all().delete()
        print("Done")
