from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from dsmr_backend.mixins import InfiniteManagementCommandMixin
import dsmr_backend.services.schedule
from dsmr_backend.models.settings import BackendSettings


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Generates a generic event triggering apps for backend operations, cron-like.')
    name = __name__  # Required for PID file.

    def initialize(self):
        self.sleep_time = BackendSettings.get_solo().process_sleep

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        dsmr_backend.services.schedule.execute_scheduled_processes()  # Future
        dsmr_backend.services.schedule.dispatch_signals()  # Legacy
