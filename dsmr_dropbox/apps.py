from django.apps import AppConfig
from django.conf import settings
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

    offset = timezone.now() - timezone.timedelta(
        minutes=settings.DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES
    )

    if dropbox_settings.next_sync > offset:
        return

    return MonitoringStatusIssue(
        __name__,
        _('Waiting for the next Dropbox sync to be executed'),
        dropbox_settings.next_sync
    )
