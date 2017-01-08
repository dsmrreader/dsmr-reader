from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from dsmr_backend.mixins import InfiniteManagementCommandMixin
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_datalogger.exceptions import InvalidTelegramChecksum
import dsmr_datalogger.services


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Performs an DSMR P1 telegram reading on the COM port.')
    name = __name__  # Required for PID file.
    sleep_time = 1

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        datalogger_settings = DataloggerSettings.get_solo()

        # This should only by disabled when performing huge migrations.
        if not datalogger_settings.track:
            raise CommandError("Datalogger tracking is DISABLED!")

        telegram = dsmr_datalogger.services.read_telegram()

        # Reflect output to STDOUT for logging and convenience.
        self.stdout.write(telegram)

        try:
            dsmr_datalogger.services.telegram_to_reading(data=telegram)
        except InvalidTelegramChecksum:
            # The service called already logs the error.
            pass
