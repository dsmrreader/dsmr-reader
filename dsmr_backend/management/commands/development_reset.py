from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.conf import settings

from dsmr_backup.models.settings import BackupSettings, DropboxSettings
from dsmr_mindergas.models.settings import MinderGasSettings


class Command(BaseCommand):
    help = _('Resets the environment for development purposes. Not intended for production.')

    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError(_('Intended usage is NOT production! Only allowed when DEBUG = True'))

        # Just wipe all settings which can affect the environment.
        BackupSettings.objects.update(daily_backup=False)
        DropboxSettings.objects.update(access_token=None)
        MinderGasSettings.objects.update(export=False, auth_token=None)
