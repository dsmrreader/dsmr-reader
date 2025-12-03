from django.core.management.base import BaseCommand, CommandError

from dsmr_mqtt.models import queue


class Command(BaseCommand):
    help = "Deletes ALL messages in the queue"

    def handle(self, **options):
        queue.Message.objects.all().delete()
        print("Done.")
