import traceback

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.utils import timezone

from dsmr_backend.mixins import InfiniteManagementCommandMixin
import dsmr_backend.signals


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Generates a generic event triggering apps for backend operations, cron-like.')
    name = __name__  # Required for PID file.

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        self.stdout.write('Broadcasting backend signal @ {}...'.format(
            timezone.localtime(timezone.now())
        ))

        # send_robust() guarantees the every listener receives this signal.
        responses = dsmr_backend.signals.backend_called.send_robust(None)
        signal_failures = []

        for current_receiver, current_response in responses:
            if isinstance(current_response, Exception):
                # Add and print traceback to help debugging any issues raised.
                exception_traceback = traceback.format_tb(current_response.__traceback__, limit=100)
                exception_traceback = "\n".join(exception_traceback)

                self.stdout.write(' - {} :: {}'.format(current_receiver, exception_traceback))
                self.stderr.write(exception_traceback)
                signal_failures.append(exception_traceback)

        if signal_failures:
            # Reflect any error to output for convenience.
            raise CommandError(signal_failures)
