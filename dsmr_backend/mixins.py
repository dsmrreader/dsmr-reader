import logging
import signal
import time
import os

import sys
import traceback

from django.core.management.base import CommandError
from django.utils import timezone
from django.utils.translation import gettext as _
from django.conf import settings
from django.contrib import admin
from django.db import connection


logger = logging.getLogger('dsmrreader')


class StopInfiniteRun(EnvironmentError):
    """ Triggers InfiniteManagementCommandMixin to stop the current loop. """
    pass


class InfiniteManagementCommandMixin:
    """ Mixin for long running management commands, only stopping (gracefully) on SIGHUP signal. """
    name = None  # Set in sub classes.
    sleep_time = None  # Set in sub classes.
    _keep_alive = None
    _pid_file = None
    _next_reconnect = None

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

        # Only tests should use this. Or when developing a command.
        if options.get('run_once'):
            logger.debug('%s: Starting (once)', self.name)
            self.run_once(**options)
        else:
            logger.debug('%s: Starting', self.name)
            self.run_loop(**options)

        self.shutdown()
        logger.debug('%s: Exited', self.name)

    def run_loop(self, **options):
        """ Runs in an infinite loop, until we're signaled to stop. """
        # Supervisor defaults to TERM and our deploy script uses HUP.
        signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # We simply keep executing the management command until we are told otherwise.
        self._keep_alive = True
        logger.debug('%s: Starting infinite command loop...', self.name)  # Just to make sure it gets printed.
        self._update_next_reconnect()

        while self._keep_alive:
            self.run_once(**options)

            # Do not hammer.
            if self.sleep_time is not None:
                logger.debug('%s: Sleeping %ss', self.name, self.sleep_time)
                time.sleep(float(self.sleep_time))  # For some reasons Decimals bug out!

            # Reconnect to database connection after a while. Ensures the database is still there. See #427
            if timezone.now() >= self._next_reconnect:
                self._update_next_reconnect()
                logger.debug('Reconnecting to database to refresh connection...')
                connection.close()

    def _update_next_reconnect(self):
        self._next_reconnect = timezone.now() + timezone.timedelta(
            seconds=settings.DSMRREADER_MAX_DATABASE_CONNECTION_SESSION_IN_SECONDS
        )

    def run_once(self, **options):
        """ Runs the management command exactly once. """
        try:
            self.run(data=self.data, **options)
        except CommandError:
            # Pass tru.
            raise
        except StopInfiniteRun:
            # Explicit exit.
            logger.info('%s: [i] Detected StopInfiniteRun exception', self.name)
            self._stop()
        except:
            # Unforeseen errors.
            _, _, exc_traceback = sys.exc_info()
            logger.error('%s: [!] Exception raised. %s', self.name, traceback.format_exc())
            self._stop()

    def initialize(self):
        """ Called once. Override and handle any initialization required. """
        return

    def shutdown(self):
        """ Called once. Override and handle any cleanup required. """
        return

    def run(self, *args, **options):
        raise NotImplementedError('Subclasses of InfiniteManagementCommandMixin must provide a run() method')

    def __del__(self):
        """ Tear down, always called on destruction. """
        if self._pid_file:
            self._remove_pid_file()

    def _signal_handler(self, signum, frame):
        # If we get called, then we must gracefully exit.
        logger.info('%s: Detected signal #%s', self.name, signum)
        self._stop()

    def _stop(self):
        """ Sets the flag for ending the command on next flag check. """
        self._keep_alive = False
        logger.info('%s: Exiting on next run...', self.name)

    def _write_pid_file(self):
        self._pid_file = os.path.join(
            settings.DSMRREADER_MANAGEMENT_COMMANDS_PID_FOLDER,
            'dsmrreader--{}.pid'.format(self.name.split('.')[-1])
        )
        with open(self._pid_file, 'w') as file_handle:
            file_handle.write(str(os.getpid()))

    def _remove_pid_file(self):
        try:
            os.unlink(self._pid_file)
        except IOError:
            pass

    def _check_logger_level(self):
        logging_level = logger.getEffectiveLevel()

        if logging_level <= logging.INFO:
            return

        print(
            'Current logging level set to "{}". More information can be found here: '
            'https://dsmr-reader.readthedocs.io/en/latest/how-to/troubleshooting/enabling-debug-logging.html'.format(
                logging.getLevelName(logging_level)
            )
        )


class ReadOnlyAdminModel(admin.ModelAdmin):
    """ Read only model for Django admin. """

    def __init__(self, *args, **kwargs):
        super(ReadOnlyAdminModel, self).__init__(*args, **kwargs)
        self.readonly_fields = [x.name for x in self.model._meta.get_fields()]

    def has_view_permission(self, request, obj=None):
        return True

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class DeletionOnlyAdminModel(ReadOnlyAdminModel):
    def has_delete_permission(self, request, obj=None):
        return True


class ChangeOnlyAdminModel(ReadOnlyAdminModel):
    def has_change_permission(self, request, obj=None):
        return True


class ModelUpdateMixin:
    """ Add update() on Django model instance, similar to queryset.update(). """

    def update(self, **updated_fields):
        if not updated_fields:
            return

        for key, value in updated_fields.items():
            setattr(self, key, value)

        self.save(update_fields=updated_fields.keys())
