import logging
import signal
import time
import os

from django.core.management.base import CommandError
from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib import admin
from django.db import connection


logger = logging.getLogger('commands')


class StopInfiniteRun(StopIteration):
    """ Triggers InfiniteManagementCommandMixin to stop the current loop. """
    pass


class InfiniteManagementCommandMixin(object):
    """ Mixin for long running management commands, only stopping (gracefully) on SIGHUP signal. """
    sleep_time = None
    _keep_alive = None
    _pid_file = None

    def add_arguments(self, parser):
        parser.add_argument(
            '--run-once',
            action='store_true',
            dest='run_once',
            default=False,
            help=_('Forces single run, overriding Infinite Command mixin')
        )

    def handle(self, **options):
        """ Called by Django to run command. We relay to run() ourselves and keep it running. """
        self._check_logger_level()
        self._write_pid_file()
        self.data = self.initialize()

        if options.get('run_once'):
            # Only tests should use this. Or when developing a command.
            self.run_once(**options)
        else:
            self.run_loop(**options)

        self.shutdown()
        logger.info('Exited')

    def run_loop(self, **options):
        """ Runs in an infinite loop, until we're signaled to stop. """
        # Supervisor defaults to TERM and our deploy script uses HUP.
        signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # We simply keep executing the management command until we are told otherwise.
        self._keep_alive = True
        logger.debug('Starting infinite command loop...')  # Just to make sure it gets printed.

        while self._keep_alive:
            self.run_once(**options)

            # Do not hammer.
            if self.sleep_time is not None:
                logger.debug('Sleeping %s sec(s)', self.sleep_time)
                time.sleep(self.sleep_time)

            # Check database connection after each run. This will force Django to reconnect as well, when having issues.
            if settings.DSMRREADER_RECONNECT_DATABASE:
                connection.close()

    def run_once(self, **options):
        """ Runs the management command exactly once. """
        try:
            self.run(data=self.data, **options)
        except CommandError:
            # Pass tru.
            raise
        except StopInfiniteRun:
            # Explicit exit.
            logger.info(' [i] Detected StopInfiniteRun exception')
            self._stop()
        except Exception as error:
            # Unforeseen errors.
            logger.error(' [!] Exception raised in run(): %s', error)

    def initialize(self):
        """ Called once. Override and handle any initialization required. """
        pass

    def shutdown(self):
        """ Called once. Override and handle any cleanup required. """
        pass

    def run(self, *args, **options):
        raise NotImplementedError('Subclasses of InfiniteManagementCommandMixin must provide a run() method')

    def __del__(self):
        """ Tear down, always called on destruction. """
        if self._pid_file:
            self._remove_pid_file()

    def _signal_handler(self, signum, frame):
        # If we get called, then we must gracefully exit.
        logger.info('Detected signal #%s', signum)
        self._stop()

    def _stop(self):
        """ Sets the flag for ending the command on next flag check. """
        self._keep_alive = False
        logger.info('Exiting on next run...')

    def _write_pid_file(self):
        self._pid_file = os.path.join(
            settings.DSMRREADER_MANAGEMENT_COMMANDS_PID_FOLDER,
            'dsmrreader--{}.pid'.format(self.name.split('.')[-1])  # Set in management command.
        )
        with open(self._pid_file, 'w') as file_handle:
            file_handle.write(str(os.getpid()))

    def _remove_pid_file(self):
        try:
            os.unlink(self._pid_file)
        except IOError:
            pass

    def _check_logger_level(self):
        # This will result in only logging errors, so make sure to clear that up.
        if logger.getEffectiveLevel() > logging.INFO:
            print(
                'The current logging level only logs warnings and errors, to reduce I/O. More information can be '
                'found here: https://dsmr-reader.readthedocs.io/en/latest/troubleshooting.html#logging'
            )


class ReadOnlyAdminModel(admin.ModelAdmin):
    """ Read only model for Django admin. """
    def __init__(self, *args, **kwargs):
        super(ReadOnlyAdminModel, self).__init__(*args, **kwargs)
        self.readonly_fields = [x.name for x in self.model._meta.get_fields()]

    def has_change_permission(self, request, obj=None):
        return True

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
