from django.core.management.base import BaseCommand

from dsmr_mqtt.models import queue


class Command(BaseCommand):
    help = "Deletes ALL MQTT messages from the queue"

    def handle(self, **options):
        queue.Message.objects.all().delete()
        print("Done")
