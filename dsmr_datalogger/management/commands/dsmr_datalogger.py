import logging

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from dsmr_backend.mixins import InfiniteManagementCommandMixin, StopInfiniteRun
import dsmr_datalogger.services.datalogger
from dsmr_datalogger.exceptions import InvalidTelegramError
from dsmr_datalogger.models.settings import DataloggerSettings


logger = logging.getLogger('dsmrreader')


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Performs an DSMR P1 telegram reading on the serial port.')
    name = __name__  # Required for PID file.

    # Persistent 'connection' to either the serial port or network socket, wrapped as generator.
    telegram_generator = None

    def initialize(self):
        self._update_sleep()
        self.telegram_generator = dsmr_datalogger.services.datalogger.get_telegram_generator()

    def run(self, **options):
        telegram = next(self.telegram_generator)

        try:
            dsmr_datalogger.services.datalogger.telegram_to_reading(data=telegram)
        except InvalidTelegramError:
            pass

        self._check_restart_required()
        self._update_sleep()

    def _update_sleep(self):
        self.sleep_time = DataloggerSettings.get_solo().process_sleep

    def _check_restart_required(self):
        if not DataloggerSettings.get_solo().restart_required:
            return

        DataloggerSettings.objects.update(restart_required=False)
        logger.warning('Detected datalogger restart required, stopping process...')
        raise StopInfiniteRun()
