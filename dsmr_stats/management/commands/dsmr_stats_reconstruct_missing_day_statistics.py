from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

import dsmr_stats.services


class Command(BaseCommand):
    help = _('Reconstructs missing day statistics by using available hour statistics')

    def handle(self, **options):
        dsmr_stats.services.reconstruct_missing_day_statistics()

        print()
        print('To recalculate prices as well, execute:   ./manage.py dsmr_stats_recalculate_prices')
