from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, **options):
        raise CommandError('Since DSMR-reader v4.x: This command has been replaced by dsmr_client')
