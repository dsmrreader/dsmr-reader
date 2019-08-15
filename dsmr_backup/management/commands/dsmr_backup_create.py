import os

from django.core.management.base import BaseCommand, CommandError

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
import dsmr_backup.services.backup


class Command(BaseCommand):
    help = 'Forces compact (statistics) backup creation.'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--full',
            action='store_true',
            dest='full',
            default=False,
            help='Whether to create a full backup'
        )
        parser.add_argument(
            '--compact',
            action='store_true',
            dest='compact',
            default=False,
            help='Whether to create a compact backup, only containing day- and hour statistics'
        )

    def handle(self, **options):
        if not options.get('full') and not options.get('compact'):
            raise CommandError('Missing --full or --compact argument')

        base_folder = dsmr_backup.services.backup.get_backup_directory()

        if options.get('full'):
            dsmr_backup.services.backup.create_full(
                folder=base_folder
            )

        if options.get('compact'):
            dsmr_backup.services.backup.create_partial(
                folder=os.path.join(base_folder, 'archive'),
                models_to_backup=(DayStatistics, HourStatistics)
            )
