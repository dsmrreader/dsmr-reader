from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.utils import timezone

from dsmr_stats.models import DsmrReading
import dsmr_stats.services


class Command(BaseCommand):
    help = 'Compacts existing DSMR readings into consumption points.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-ago', '-d', nargs='+', type=str, dest='days_ago', default=1
        )

    def handle(self, **options):
        try:
            readings = self._fetch(**options)
            self._compact(readings)
        except Exception as error:
            raise CommandError(error)

    def _fetch(self, **options):
        """ Finds all readings in the eglible for compacting. """
        max_timestamp = timezone.now() - timezone.timedelta(days=options['days_ago'])
        print(_('Only selecting reading before: {}'.format(max_timestamp)))

        unprocessed_readings = DsmrReading.objects.filter(
            processed=False, timestamp__lt=max_timestamp
        )
        print(_('Found {} readings to compact'.format(unprocessed_readings.count())))
        return unprocessed_readings

    def _compact(self, readings):
#         readings = readings[0:50]
        readings = [readings[0]]

        for current_reading in readings:
            print(_('Compacting: {}'.format(current_reading)))
            dsmr_stats.services.compact(dsmr_reading=current_reading)
