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
        self.stdout.write('')
        self.stdout.write('Broadcasting backend signal @ {}...'.format(timezone.now()))

        # send_robust() guarantees the every listener receives this signal.
        responses = dsmr_backend.signals.backend_called.send_robust(None)

        signal_failure = []

        for current_receiver, current_response in responses:
            self.stdout.write(' - {} :: {}'.format(current_receiver, current_response))

            if isinstance(current_response, Exception):
                signal_failure.append(current_response)

        if signal_failure:
            # Reflect any error to output for convenience.
            raise CommandError(signal_failure)
