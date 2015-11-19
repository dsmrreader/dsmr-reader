from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.utils import timezone

from dsmr_stats.models import DsmrReading


class Command(BaseCommand):
    help = 'Cleans up any source data from the poller. PERMANENTLY DELETES DATA!'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            metavar='DAYS',
            dest='days',
            default=365,
            help='Any polled source data older then DAYS will be purged (default %(default)s days).'
        )
        parser.add_argument(
            '--noinput',
            type=bool,
            metavar='',
            dest='no_input',
            default=False,
            help='Tells Django to NOT prompt the user for input of any kind.'
        )

    def handle(self, **options):
        cleanup_date = timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
        cleanup_date = cleanup_date - timezone.timedelta(days=options['days'])

        if not options.get('no_input'):
            self._confirm(cleanup_date)

        self._cleanup(cleanup_date)

    def _confirm(self, cleanup_date):
        try:
            read = input(
                'WARNING: This will PERMANENTLY DELETE SOURCE DATA before "{}, still continue?'
                ' yes/no: '.format(cleanup_date)
            )
        except KeyboardInterrupt:
            read = None

        if read != 'yes':
            raise CommandError('Aborted by user')

    def _cleanup(self, cleanup_date):
        data_to_delete = DsmrReading.objects.filter(timestamp__lt=cleanup_date)
        print('Found {} records to delete'.format(data_to_delete.count()))

        data_to_delete.delete()
        print('Deleted {} records'.format(data_to_delete.count()))
