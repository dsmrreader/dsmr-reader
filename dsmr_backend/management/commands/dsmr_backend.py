import logging

from django.core.management.base import BaseCommand

from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.mixins import InfiniteManagementCommandMixin, StopInfiniteRun
import dsmr_backend.services.persistent_clients
import dsmr_backend.services.schedule


logger = logging.getLogger('commands')


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = 'Backend operations in a persistent process'
    name = __name__  # Required for PID file.

    # Persistent during this process' lifetime.
    persistent_clients = None

    def initialize(self):
        self.sleep_time = BackendSettings.get_solo().process_sleep

        self.persistent_clients = dsmr_backend.services.persistent_clients.initialize()
        logger.debug('Persistent clients initialized: %s', [x.__class__ for x in self.persistent_clients])

    def shutdown(self):
        """ Disconnects the client(s) gracefully. """
        dsmr_backend.services.persistent_clients.terminate(self.persistent_clients)

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        dsmr_backend.services.schedule.execute_scheduled_processes()
        dsmr_backend.services.schedule.dispatch_signals()  # Legacy

        if self.persistent_clients:
            dsmr_backend.services.persistent_clients.run(self.persistent_clients)

        if BackendSettings.get_solo().restart_required:
            BackendSettings.objects.update(restart_required=False)
            logger.warning('Detected restart required, stopping process...')
            raise StopInfiniteRun()
