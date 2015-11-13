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
            '--days-ago', '-d', type=int, dest='days_ago', default=1
        )
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
        max_timestamp = timezone.now() - timezone.timedelta(days=options['days_ago'])
        max_readings = options['max_readings']
        print(_('Only selecting reading before: {} (max {})'.format(max_timestamp, max_readings)))

        unprocessed_readings = DsmrReading.objects.filter(
            processed=False, timestamp__lt=max_timestamp
        )
        print(_('Found {} readings to compact'.format(unprocessed_readings.count())))

        # Limit resultset, as we should compact much faster than new readings
        # being created (~ every 11 seconds).
        return unprocessed_readings[0:max_readings]

    def _compact(self, readings):
        for current_reading in readings:
            print(_('Compacting: {}'.format(current_reading)))
            dsmr_stats.services.compact(dsmr_reading=current_reading)
