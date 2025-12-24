import logging

from django.core.management.base import BaseCommand
from django.conf import settings

from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.mixins import InfiniteManagementCommandMixin, StopInfiniteRun
import dsmr_backend.services.persistent_clients
import dsmr_backend.services.schedule


logger = logging.getLogger("dsmrreader")


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = "Backend operations in a persistent process"
    name = __name__  # Required for PID file.

    # Persistent during this process' lifetime.
    persistent_clients = None

    def initialize(self):
        self.sleep_time = BackendSettings.get_solo().process_sleep

        self.persistent_clients = dsmr_backend.services.persistent_clients.initialize()
        logger.debug(
            "Persistent clients initialized: %s",
            [x.__class__ for x in self.persistent_clients],
        )

    def shutdown(self):
        """Disconnects the client(s) gracefully."""
        dsmr_backend.services.persistent_clients.terminate(self.persistent_clients)

    def run(self, **options):
        """InfiniteManagementCommandMixin listens to handle() and calls run() in a loop."""
        self._check_hibernation()

        dsmr_backend.services.schedule.execute_scheduled_processes()
        dsmr_backend.services.schedule.dispatch_signals()  # Legacy

        if self.persistent_clients:
            dsmr_backend.services.persistent_clients.run(self.persistent_clients)

        self._check_restart_required()

    def _check_hibernation(self):
        """
        Checks whether the process has a directive to never run and just hibernate.

        This can be used to prevent new installations using a backup from disrupting some centralize processes outside
        DSMR-reader (e.g. Dropbox, MQTT, etc).
        """
        if not settings.DSMRREADER_BACKEND_HIBERNATE:
            return

        BackendSettings.objects.update(restart_required=False)
        logger.critical("Detected backend hibernation (DSMRREADER_BACKEND_HIBERNATE), stopping process...")
        raise StopInfiniteRun()

    def _check_restart_required(self):
        """Checks whether a restart has been requested and stops the process if so."""
        if not BackendSettings.get_solo().restart_required:
            return

        BackendSettings.objects.update(restart_required=False)
        logger.warning("Detected backend restart required, stopping process...")
        raise StopInfiniteRun()
