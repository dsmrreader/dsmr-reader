from time import sleep

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.utils import timezone

from dsmr_stats.models import DsmrReading
import dsmr_stats.services


class Command(BaseCommand):
    help = 'Compacts existing DSMR readings into consumption points.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-readings', '-m', type=int, dest='max_readings', default=360
        )

    def handle(self, **options):
        try:
            readings = self._fetch(**options)
            self._compact(readings)
        except Exception as error:
            raise CommandError(error)

        # Allow supervisor to mark this process as OK.
        sleep(1)

    def _fetch(self, **options):
        """ Finds all readings in the eglible for compacting. """
        max_readings = options['max_readings']

        unprocessed_readings = DsmrReading.objects.filter(
            processed=False, timestamp__lt=timezone.now()
        )
        print(_('Found {} readings to compact'.format(unprocessed_readings.count())))

        # Limit resultset, as we should compact much faster than new readings
        # being created (~ every 11 seconds).
        print(_('Limiting readings for this run at: {}'.format(max_readings)))
        return unprocessed_readings[0:max_readings]

    def _compact(self, readings):
        for current_reading in readings:
            print(_('Compacting: {}'.format(current_reading)))
            dsmr_stats.services.compact(dsmr_reading=current_reading)
