import os

from django.core.management.base import BaseCommand, CommandError

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
import dsmr_backup.services.backup


class Command(BaseCommand):
    help = "Forces compact (statistics) backup creation."

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--full",
            action="store_true",
            dest="full",
            default=False,
            help="Whether to create a full backup",
        )
        parser.add_argument(
            "--compact",
            action="store_true",
            dest="compact",
            default=False,
            help="Whether to create a compact backup, only containing day- and hour statistics",
        )

    def handle(self, **options):
        if not options.get("full") and not options.get("compact"):
            raise CommandError("Missing --full or --compact argument")

        base_folder = os.path.join(
            dsmr_backup.services.backup.get_backup_directory(), "manually"
        )

        if options.get("full"):
            backup_file = dsmr_backup.services.backup.create_full(folder=base_folder)
            print("Created full backup:", backup_file)

        if options.get("compact"):
            backup_file = dsmr_backup.services.backup.create_partial(
                folder=base_folder, models_to_backup=(DayStatistics, HourStatistics)
            )
            print("Created partial backup:", backup_file)
