from django.core.management.base import BaseCommand

import dsmr_stats.services


class Command(BaseCommand):
    help = "Retroactively recalculates DayStatistics totals using stored meter positions (fixes #1770)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--write",
            action="store_false",
            dest="dry_run",
            default=True,
            help="Write recalculated values to the database (default is dry-run / preview only).",
        )

    def handle(self, **options) -> None:
        dsmr_stats.services.recalculate_statistics_from_meter_positions(dry_run=options["dry_run"])
        if not options["dry_run"]:
            print("\nPrices recalculated in the same pass — no need to run dsmr_stats_recalculate_prices separately.")
        else:
            print("\nDry run complete. Re-run with --write to apply changes.")
