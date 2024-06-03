from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

import dsmr_stats.services


class Command(BaseCommand):
    help = "Deletes all (generated) data in the STATS app, for development purposes. Not intended for production."

    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError(
                "Intended usage is NOT production! Only allowed when DEBUG = True"
            )

        dsmr_stats.services.clear_statistics()
