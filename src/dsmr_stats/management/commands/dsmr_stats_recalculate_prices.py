from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from dsmr_backend.mixins import add_batch_size_argument
import dsmr_stats.repair_services


class Command(BaseCommand):
    help = _("Recalculates day statistics prices")

    def add_arguments(self, parser) -> None:
        add_batch_size_argument(parser)

    def handle(self, **options):
        dsmr_stats.repair_services.recalculate_prices(batch_size=options["batch_size"])
