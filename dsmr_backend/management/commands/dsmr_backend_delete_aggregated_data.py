from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

import dsmr_consumption.services
import dsmr_stats.services
from dsmr_datalogger.models.reading import DsmrReading


class Command(BaseCommand):
    help = _(
        'Deletes all aggregated data generated. Such as consumption and (day/hour) statistics. '
        'This command does NOT affect any readings stored. In fact, you should NEVER run this, unless you still have '
        'each and EVERY reading stored, as the application will attempt to recalculate all aggregated data deleted '
        'retroactively, using each reading stored.')

    def handle(self, **options):
        print(' - Clearing consumption data')
        dsmr_consumption.services.clear_consumption()

        print(' - Clearing statistics')
        dsmr_stats.services.clear_statistics()

        print(' - Resetting state of all readings for processing (might take a while)')
        DsmrReading.objects.all().update(processed=False)

        self.stdout.write('Command completed.')
