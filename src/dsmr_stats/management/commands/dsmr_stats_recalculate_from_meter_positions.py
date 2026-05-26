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
        parser.add_argument(
            "--analyze",
            action="store_true",
            dest="analyze",
            default=False,
            help=(
                "Analyse data quality only (read-only): checks DayStatistics against consecutive meter-position "
                "deltas, and HourStatistics sums against DayStatistics totals. Cannot be combined with --days, "
                "--hours, or --write."
            ),
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            dest="batch_size",
            default=None,
            help="Number of records to process per batch (default: 365 for --days, 168 for --hours).",
        )

    def handle(self, **options) -> None:
        dry_run = options["dry_run"]
        run_days = options["days"]
        run_hours = options["hours"]
        run_analyze = options["analyze"]
        batch_size = options["batch_size"]

        if run_analyze:
            if run_days or run_hours or not dry_run:
                self.stderr.write("Error: --analyze cannot be combined with --days, --hours, or --write.")
                return
            dsmr_stats.repair_services.analyze_data_quality()
            return

        if not run_days and not run_hours:
            self.stderr.write("Error: specify --days, --hours, or --analyze.")
            return

        if run_days and run_hours:
            self.stderr.write("Error: specify --days or --hours, not both.")
            return

        print("Starting — this may take a few minutes before any progress is shown...\n")

        if run_days:
            kwargs = {"dry_run": dry_run}
            if batch_size is not None:
                kwargs["batch_size"] = batch_size
            dsmr_stats.repair_services.recalculate_statistics_from_meter_positions(**kwargs)
            if not dry_run:
                print(
                    "\nPrices recalculated in the same pass — no need to run dsmr_stats_recalculate_prices separately."
                )
            else:
                print("\nDry run complete. Re-run with --write to apply changes.")

        if run_hours:
            kwargs = {"dry_run": dry_run}
            if batch_size is not None:
                kwargs["batch_size"] = batch_size
            dsmr_stats.repair_services.recalculate_hour_statistics(**kwargs)
