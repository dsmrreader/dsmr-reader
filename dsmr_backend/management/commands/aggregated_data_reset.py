from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _
from django.conf import settings

import dsmr_consumption.services
import dsmr_stats.services
from dsmr_datalogger.models.reading import DsmrReading


class Command(BaseCommand):
    help = _(
        "DELETES all aggregated data for development purposes. Not intended for production."
    )

    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError(
                _("Intended usage is NOT production! Only allowed when DEBUG = True")
            )

        # Delete all calculated data.
        dsmr_stats.services.clear_statistics()
        dsmr_consumption.services.clear_consumption()

        # Flag all readings for reprocessing.
        DsmrReading.objects.all().update(processed=False)
