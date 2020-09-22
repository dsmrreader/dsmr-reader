from django.apps import AppConfig
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backend.signals import request_status


class DropboxAppConfig(AppConfig):
    name = 'dsmr_dropbox'
    verbose_name = _('Dropbox')


@receiver(request_status)
def check_dropbox_sync(**kwargs):
    from dsmr_backup.models.settings import DropboxSettings

    dropbox_settings = DropboxSettings.get_solo()

    if not dropbox_settings.access_token:
        return

    offset = timezone.now() - timezone.timedelta(hours=1)

    if dropbox_settings.next_sync > offset:
        return

    return MonitoringStatusIssue(
        __name__,
        'Dropbox sync took too long',
        dropbox_settings.next_sync
    )
