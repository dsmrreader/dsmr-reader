from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

import dsmr_backend.signals


class Command(BaseCommand):
    help = _('Generates a generic event triggering apps for backend operations, cron-like.')

    def handle(self, **options):
        self.stdout.write('Broadcasting "backend_called" signal...')

        # send_robust() guarantees the every listener receives this signal.
        responses = dsmr_backend.signals.backend_called.send_robust(None)

        for current_app, current_response in responses:
            # Reflect any error to output for convenience.
            if isinstance(current_response, Exception):
                raise CommandError('Exception @ {}: {}'.format(current_app, current_response))

        self.stdout.write('Finished.')
