from django.core.management.base import BaseCommand

import dsmr_stats.services


class Command(BaseCommand):
    help = "Reconstructs missing day statistics (e.g.: after importing legacy data)"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--batch-size",
            type=int,
            dest="batch_size",
            default=365,
            help="Number of days to process per batch (default: 365).",
        )

    def handle(self, **options):
        dsmr_stats.services.reconstruct_missing_day_statistics(batch_size=options["batch_size"])

        print()
        print("To recalculate prices as well, execute:   ./manage.py dsmr_stats_recalculate_prices")
