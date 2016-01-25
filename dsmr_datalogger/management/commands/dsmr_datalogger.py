from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

import dsmr_datalogger.services


class Command(BaseCommand):
    help = _('performs an DSMR P1 telegram reading on the COM port.')

    def handle(self, **options):
        telegram = dsmr_datalogger.services.read_telegram()
        dsmr_datalogger.services.telegram_to_reading(data=telegram)
