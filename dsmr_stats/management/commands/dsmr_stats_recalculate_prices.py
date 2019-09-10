from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

import dsmr_stats.services


class Command(BaseCommand):
    help = _('Recalculates day statistics prices')

    def handle(self, **options):
        dsmr_stats.services.recalculate_prices()
