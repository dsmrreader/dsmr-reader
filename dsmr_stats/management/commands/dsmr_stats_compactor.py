from time import sleep

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.db import transaction

from dsmr_stats.models import DsmrReading
import dsmr_stats.services
from dsmr_stats.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.models.statistics import ElectricityStatistics


class Command(BaseCommand):
    help = _('Compacts existing DSMR readings into consumption points.')
    GROUPING_SECOND = 'second'
    GROUPING_MINUTE = 'minute'

    def add_arguments(self, parser):
        parser.add_argument(
            '--max-readings',
            '-m',
            type=int,
            dest='max_readings',
            default=1080,
            help=_('The max number of readings to compact this run (default: %(default)s)')
        )
        parser.add_argument(
            '--group-by-minute',
            action='store_true',
            dest='group_by_minute',
            default=False,
            help=_('Precision of compacting ELECTRICITY readings (default: %(default)s)')
        )
        parser.add_argument(
            '--purge',
            action='store_true',
            dest='purge',
            default=False,
            help=_(
                'Purges all consumption data (DELETES IT!) and marks all readings as unprocessed.'
                'Only use this when changing compact grouping AND YOU HAVE ALL HISTORIC READINGS!'
            )
        )

    def handle(self, **options):
        # Purging all data is a whole other path, so we will stop after performing the task.
        if options['purge']:
            self._purge_and_reset()
            raise CommandError("Purge & reset completed")

        group_by_minute = options['group_by_minute']
        print(_('Grouping electricity readings by minute? {}'.format(group_by_minute)))

        try:
            readings = self._fetch(**options)
            self._compact(readings, group_by_minute)
        except Exception as error:
            raise CommandError(error)

        # Allow supervisor to mark this process as OK.
        sleep(1)

    @transaction.atomic
    def _purge_and_reset(self):
        """ Purges all consumption data, including statistics, and reverts reading processing. """
        es = ElectricityStatistics.objects.all()
        print(_('Deleting {} ElectricityStatistics record(s)').format(es.count()))
        es.delete()

        ec = ElectricityConsumption.objects.all()
        print(_('Deleting {} ElectricityConsumption record(s)').format(ec.count()))
        ec.delete()

        eg = GasConsumption.objects.all()
        print(_('Deleting {} GasConsumption record(s)').format(eg.count()))
        eg.delete()

        dr = DsmrReading.objects.processed()
        print(_('Resetting {} DsmrReading record(s)').format(dr.count()))
        dr.update(processed=False)

    def _fetch(self, **options):
        """ Finds all readings in the eglible for compacting. """
        unprocessed_readings = DsmrReading.objects.filter(
            processed=False, timestamp__lt=timezone.now()
        )
        print(_('Found {} readings to compact'.format(unprocessed_readings.count())))

        # Limit result set, as we should compact much faster than new readings
        # being created (~ every 11 seconds).
        max_readings = options['max_readings']
        print(_('Limiting readings for this run at: {}'.format(max_readings)))
        return unprocessed_readings[0:max_readings]

    def _compact(self, readings, group_by_minute):

        for current_reading in readings:
            print(_('Compacting: {}'.format(current_reading)))
            dsmr_stats.services.compact(
                dsmr_reading=current_reading,
                group_by_minute=group_by_minute
            )
