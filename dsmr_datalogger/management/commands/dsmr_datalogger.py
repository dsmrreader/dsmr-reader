from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _

from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_datalogger.services


class Command(BaseCommand):
    help = _('Performs an DSMR P1 telegram reading on the COM port.')

    def handle(self, **options):
        datalogger_settings = DataloggerSettings.get_solo()

        # This should only by disabled when performing huge migrations.
        if not datalogger_settings.track:
            raise CommandError("Datalogger tracking is DISABLED!")

        telegram = dsmr_datalogger.services.read_telegram()

        # Reflect output to STDOUT for logging and convenience.
        self.stdout.write(telegram)

        dsmr_datalogger.services.telegram_to_reading(data=telegram)
