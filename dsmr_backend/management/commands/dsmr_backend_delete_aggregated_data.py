from django.core.management.base import BaseCommand

import dsmr_consumption.services
import dsmr_stats.services
from dsmr_datalogger.models.reading import DsmrReading


class Command(BaseCommand):
    help = (
        'Deletes all aggregated data generated. This command does NOT affect any readings stored.'
        'In fact, you should NEVER run this, unless you still have each and EVERY reading stored, '
        'as the application will attempt to recalculate all aggregated data deleted retroactively.'
    )

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--consumption',
            action='store_true',
            dest='consumption',
            default=False,
            help='Clear aggregated consumption'
        )
        parser.add_argument(
            '--statistics',
            action='store_true',
            dest='statistics',
            default=False,
            help='Clear aggregated statistics'
        )
        parser.add_argument(
            '--readings',
            action='store_true',
            dest='readings',
            default=False,
            help='Reset the processed state of readings'
        )

    def handle(self, **options):
        if options.get('consumption'):
            print(' - Clearing consumption data')
            dsmr_consumption.services.clear_consumption()
        else:
            print(' - Skipped consumption data')

        if options.get('statistics'):
            print(' - Clearing statistics')
            dsmr_stats.services.clear_statistics()
        else:
            print(' - Skipped statistics')

        if options.get('readings'):
            print(' - Resetting state of all readings for processing (might take a while)')
            DsmrReading.objects.processed().update(processed=False)
        else:
            print(' - Skipped readings')
