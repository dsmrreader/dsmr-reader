#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging

from dsmr_backend.models.settings import BackendSettings
from dsmr_backend.mixins import InfiniteManagementCommandMixin, StopInfiniteRun
import dsmr_backend.services.persistent_clients
import dsmr_backend.services.schedule


logger = logging.getLogger('dsmrreader')


class backend_runner(InfiniteManagementCommandMixin):
    def __init__(self):
        """ class-based initializor """
        # Persistent during this process' lifetime.
        self.persistent_clients = None
        self.name = __name__  # Required for PID file.

        self.initialize()

    def __enter__(self):
        """ wrapper for with-statement-executability """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """ wrapper for with-statement-executability """
        self.shutdown()

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

        self._check_restart_required()

    def _check_restart_required(self):
        if not BackendSettings.get_solo().restart_required:
            return

        BackendSettings.objects.update(restart_required=False)
        logger.warning('Detected backend restart required, stopping process...')
        raise StopInfiniteRun()


def run_mule(**options):
    # 'with' statement ensures graceful cleanup by utilizing __exit__
    print("running mule")
    with backend_runner() as backend_runner_obj:
        backend_runner_obj.handle(**options)
    print("done")


if __name__ == "__main__":
    run_mule()
