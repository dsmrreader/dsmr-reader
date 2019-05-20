from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.conf import settings

from dsmr_backend.mixins import InfiniteManagementCommandMixin
import dsmr_backend.services.schedule


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Generates a generic event triggering apps for backend operations, cron-like.')
    name = __name__  # Required for PID file.
    sleep_time = settings.DSMRREADER_BACKEND_SLEEP

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        dsmr_backend.services.schedule.execute_scheduled_processes()
        dsmr_backend.services.schedule.dispatch_signals()
