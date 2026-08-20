from django.core.management.base import BaseCommand

from dsmr_backend.mixins import add_batch_size_argument
import dsmr_stats.services


class Command(BaseCommand):
    help = "Reconstructs missing day statistics (e.g.: after importing legacy data)"

    def add_arguments(self, parser) -> None:
        add_batch_size_argument(parser, unit="days")

    def handle(self, **options):
        dsmr_stats.services.reconstruct_missing_day_statistics(batch_size=options["batch_size"])

        print()
        print("To recalculate prices as well, execute:   ./manage.py dsmr_stats_recalculate_prices")
