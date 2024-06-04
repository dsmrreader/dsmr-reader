import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from dsmr_backend.mixins import InfiniteManagementCommandMixin, StopInfiniteRun
import dsmr_datalogger.services.datalogger
from dsmr_datalogger.exceptions import InvalidTelegramError
from dsmr_datalogger.models.settings import DataloggerSettings


logger = logging.getLogger("dsmrreader")


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _("Performs an DSMR P1 telegram reading on the serial port.")
    name = __name__  # Required for PID file.

    telegram_generator = None

    def initialize(self):
        self.sleep_time = DataloggerSettings.get_solo().process_sleep

    def run(self, **options):
        if not self.telegram_generator:  # pragma: nocover
            self.telegram_generator = self._datasource()

        telegram = next(self.telegram_generator)

        # Do not persist connections when the sleep is too high.
        if self.sleep_time >= settings.DSMRREADER_DATALOGGER_MIN_SLEEP_FOR_RECONNECT:
            self.telegram_generator = None

        try:
            dsmr_datalogger.services.datalogger.telegram_to_reading(data=telegram)
        except InvalidTelegramError:
            pass

        self._check_restart_required()

    def _check_restart_required(self):
        if not DataloggerSettings.get_solo().restart_required:
            return

        DataloggerSettings.objects.update(restart_required=False)
        logger.warning("Detected datalogger restart required, stopping process...")
        raise StopInfiniteRun()

    def _datasource(self):
        return dsmr_datalogger.services.datalogger.get_telegram_generator()
