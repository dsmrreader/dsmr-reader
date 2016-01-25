import warnings

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from django.core.management import call_command


class Command(BaseCommand):
    help = _('Compacts existing DSMR readings into consumption points.')

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
            help=_('DEPRECATED: Moved to settings in database.')
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
        # Temporary for backwards compatibility
        warnings.showwarning(
            _('dsmr_stats_compactor is DEPRECATED, and will be REMOVED in v1.0, please use dsmr_backend'),
            DeprecationWarning, __file__, 0
        )

        call_command("dsmr_backend", **options)
