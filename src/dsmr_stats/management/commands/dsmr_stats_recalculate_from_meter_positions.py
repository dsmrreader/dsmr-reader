from django.core.management.base import BaseCommand

import dsmr_stats.repair_services


class Command(BaseCommand):
    help = "Retroactively recalculates DayStatistics and/or HourStatistics electricity totals (fixes #1770)."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--write",
            action="store_false",
            dest="dry_run",
            default=True,
            help="Write recalculated values to the database (default is dry-run / preview only).",
        )
        parser.add_argument(
            "--days",
            action="store_true",
            dest="days",
            default=False,
            help="Retroactively recalculate DayStatistics electricity totals from stored meter positions.",
        )
        parser.add_argument(
            "--hours",
            action="store_true",
            dest="hours",
            default=False,
            help="Retroactively recalculate HourStatistics electricity totals using cross-boundary anchors.",
        )

    def handle(self, **options) -> None:
        dry_run = options["dry_run"]
        run_days = options["days"]
        run_hours = options["hours"]

        if not run_days and not run_hours:
            self.stderr.write("Error: specify --days or --hours (not both).")
            return

        if run_days and run_hours:
            self.stderr.write("Error: specify --days or --hours, not both.")
            return

        if run_days:
            dsmr_stats.repair_services.recalculate_statistics_from_meter_positions(dry_run=dry_run)
            if not dry_run:
                print(
                    "\nPrices recalculated in the same pass — no need to run dsmr_stats_recalculate_prices separately."
                )
            else:
                print("\nDry run complete. Re-run with --write to apply changes.")

        if run_hours:
            dsmr_stats.repair_services.recalculate_hour_statistics(dry_run=dry_run)
