from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.utils import timezone

from dsmr_backup.models.settings import DropboxSettings
import dsmr_dropbox.services


class Command(BaseCommand):
    help = _('Forces Dropbox sync.')

    def handle(self, **options):
        DropboxSettings.objects.all().update(next_sync=timezone.now())
        dsmr_dropbox.services.sync()
