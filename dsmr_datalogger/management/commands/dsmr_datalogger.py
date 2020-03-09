import logging

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from dsmr_backend.mixins import InfiniteManagementCommandMixin
import dsmr_datalogger.services.datalogger
from dsmr_datalogger.models.settings import DataloggerSettings

logger = logging.getLogger('commands')


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Performs an DSMR P1 telegram reading on the serial port.')
    name = __name__  # Required for PID file.

    def initialize(self):
        self.sleep_time = DataloggerSettings.get_solo().process_sleep

    def run(self, **options):
        dsmr_datalogger.services.datalogger.read_and_process_telegram()
