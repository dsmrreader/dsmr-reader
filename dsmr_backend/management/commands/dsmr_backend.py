from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

import dsmr_backend.signals


class Command(BaseCommand):
    help = _('Generates a generic event triggering apps for backend operations, cron-like.')

    def handle(self, **options):
        self.stdout.write('Broadcasting backend signal...')

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
