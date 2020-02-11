import logging

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from dsmr_backend.mixins import InfiniteManagementCommandMixin
import dsmr_datalogger.services
from dsmr_datalogger.models.settings import DataloggerSettings

logger = logging.getLogger('commands')


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Performs an DSMR P1 telegram reading on the serial port.')
    name = __name__  # Required for PID file.

    def get_generator_function(self):
        """ Generator implementation to keep the serial connection open. """
        return dsmr_datalogger.services.read_and_process_telegram

    def initialize(self):
        self.sleep_time = DataloggerSettings.get_solo().process_sleep

    def run(self, **options):
        # Unused for this command. Using generator instead.
        pass  # pragma: no cover
