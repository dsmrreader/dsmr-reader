import signal
import time
import sys
import os

from django.utils.translation import ugettext as _
from django.conf import settings
from django.contrib import admin
from django.db import connection


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

    def __del__(self):
        if self._pid_file:
            self._remove_pid_file()

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

    def handle(self, **options):
        """ Called by Django to run command. We relay to run() ourselves and keep it running. """
        if options.get('run_once'):
            # Only tests should use this.
            return self.run(**options)

        self._write_pid_file()

        # Supervisor defaults to TERM and our deploy script uses HUP.
        signal.signal(signal.SIGHUP, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # We simply keep executing the management command until we are told otherwise.
        self._keep_alive = True
        print('Starting infinite command loop...')  # Just to make sure it gets printed.

        while self._keep_alive:
            self.run(**options)

            if self.sleep_time is not None:
                self.stdout.write('Command completed. Sleeping for {} second(s)...'.format(self.sleep_time))
                self.stdout.write('')
                time.sleep(self.sleep_time)  # Do not hammer.

            # Check database connection after each run. This will force Django to reconnect as well, when having issues.
            if settings.DSMRREADER_RECONNECT_DATABASE:
                connection.close()

        self.stdout.write('Exited due to signal detection')
        sys.exit(0)

    def run(self, *args, **options):
        raise NotImplementedError('Subclasses of InfiniteManagementCommandMixin must provide a run() method')

    def _signal_handler(self, signum, frame):
        # If we get called, then we must gracefully exit.
        self._keep_alive = False
        self.stdout.write('Detected signal #{}, exiting on next run...'.format(signum))


class ReadOnlyAdminModel(admin.ModelAdmin):
    """ Read only model for Django admin. """
    def __init__(self, *args, **kwargs):
        super(ReadOnlyAdminModel, self).__init__(*args, **kwargs)
        self.readonly_fields = [x.name for x in self.model._meta.get_fields()]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
