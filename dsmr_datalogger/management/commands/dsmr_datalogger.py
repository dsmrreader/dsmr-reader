import logging

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from django.conf import settings

from dsmr_backend.mixins import InfiniteManagementCommandMixin
from dsmr_datalogger.exceptions import InvalidTelegramError
import dsmr_datalogger.services


logger = logging.getLogger('commands')


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Performs an DSMR P1 telegram reading on the COM port.')
    name = __name__  # Required for PID file.
    sleep_time = settings.DSMRREADER_DATALOGGER_SLEEP

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        telegram = dsmr_datalogger.services.read_telegram()
        logger.info("\n%s", telegram)

        try:
            dsmr_datalogger.services.telegram_to_reading(data=telegram)
        except InvalidTelegramError:
            # The service called already logs the error.
            pass
