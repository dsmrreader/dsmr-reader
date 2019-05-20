import tempfile
import logging

from django.utils.translation import ugettext_lazy as _
from django.utils import translation, timezone

from dsmr_backup.models.settings import EmailBackupSettings
from dsmr_backend.models.settings import BackendSettings, EmailSettings
import dsmr_backend.services.email
import dsmr_backup.services.backup


logger = logging.getLogger('commands')


def run(scheduled_process):
    """ Creates a new statistics backup and sends it per email. """
    email_backup_settings = EmailBackupSettings.get_solo()

    if not email_backup_settings.interval:
        logger.debug(' - Email backup interval not set, skipping backup for a day')
        return scheduled_process.delay(timezone.timedelta(days=1))

    temp_dir = tempfile.TemporaryDirectory()
    backup_file = dsmr_backup.services.backup.create_statistics_backup(folder=temp_dir.name)

    with translation.override(language=BackendSettings.get_solo().language):
        subject = _('DSMR-reader day/hour statistics backup')
        body = _('This is an automated email, containing a backup of the day and hour statistics in the attachment.')

    email_settings = EmailSettings.get_solo()
    dsmr_backend.services.email.send(
        to=email_settings.email_to,
        subject=subject,
        body=body,
        attachment=backup_file
    )

    scheduled_process.delay(timezone.timedelta(days=email_backup_settings.interval))
