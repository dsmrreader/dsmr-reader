import traceback

from raven.contrib.django.raven_compat.models import client as raven_client
from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings

from dsmr_backend.mixins import InfiniteManagementCommandMixin
import dsmr_backend.signals


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Generates a generic event triggering apps for backend operations, cron-like.')
    name = __name__  # Required for PID file.
    sleep_time = settings.DSMRREADER_BACKEND_SLEEP

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        self.stdout.write('{}: Calling backend services'.format(timezone.localtime(timezone.now())))

        # send_robust() guarantees the every listener receives this signal.
        responses = dsmr_backend.signals.backend_called.send_robust(None)
        signal_failures = []

        for current_receiver, current_response in responses:
            if isinstance(current_response, Exception):
                try:
                    # Raven should capture each exception encountered (below).
                    raise current_response
                except Exception:
                    raven_client.captureException()

                # Add and print traceback to help debugging any issues raised.
                exception_traceback = traceback.format_tb(current_response.__traceback__, limit=100)
                exception_traceback = "\n".join(exception_traceback)

                self.stdout.write(' >>> Uncaught exception :: {}'.format(current_response))
                self.stdout.write(' >>> {} :: {}'.format(current_receiver, exception_traceback))
                self.stderr.write(exception_traceback)
                signal_failures.append(exception_traceback)
