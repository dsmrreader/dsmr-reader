from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    def handle(self, **options):
        raise CommandError('This command has been merged with dsmr_backend since DSMR-reader v4.x')
