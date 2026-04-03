from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

import dsmr_stats.repair_services


class Command(BaseCommand):
    help = _("Recalculates day statistics prices")

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--batch-size",
            type=int,
            dest="batch_size",
            default=365,
            help="Number of records to process per batch (default: 365).",
        )

    def handle(self, **options):
        dsmr_stats.repair_services.recalculate_prices(batch_size=options["batch_size"])
