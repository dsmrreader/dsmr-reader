import signal
import time
import sys
import os

from django.conf import settings


class InfiniteManagementCommandMixin(object):
    """ Mixin for long running management commands, only stopping (gracefully) on SIGHUP signal. """
    keep_alive = None
    _pid_file = None

    def __del__(self):
        self._remove_pid_file()

    def _write_pid_file(self):
        self._pid_file = os.path.join(
            settings.DSMR_MANAGEMENT_COMMANDS_PID_FOLDER,
            'dsmrreader--{}.pid'.format(self.name.split('.')[-1])  # Set in management command.
        )
        with open(self._pid_file, 'w') as file_handle:
            file_handle.write(str(os.getpid()))

    def _remove_pid_file(self):
        try:
            os.unlink(self._pid_file)
        except IOError:
            pass

    def handle(self, **options):
        """ Called by Django to run command. We relay to run() ourselves and keep it running. """
        self._write_pid_file()

        # Supervisor defaults to TERM and our deploy script uses HUP.
        signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # We simply keep executing the management command until we are told otherwise.
        self.keep_alive = True

        while self.keep_alive:
            self.run(**options)
            time.sleep(1)  # Do not hammer.

        self.stderr.write('Exited due to signal detection')
        sys.exit(0)

    def run(self, *args, **options):
        raise NotImplementedError(
            'Subclasses of InfiniteManagementCommandMixin must provide a run() method'
        )

    def _signal_handler(self, signum, frame):
        # If we get called, then we must gracefully exit.
        self.keep_alive = False
        self.stderr.write('Detected signal #{}, exiting on next run...'.format(signum))
