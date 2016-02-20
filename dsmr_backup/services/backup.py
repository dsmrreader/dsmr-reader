import os

from django.utils import timezone
from django.conf import settings

from dsmr_backup.models.settings import BackupSettings
import dsmr_backup.services.dropbox


def check():
    """ Checks whether a new backup should be created. Creates one if needed as well. """
    backup_settings = BackupSettings.get_solo()

    # Skip when backups disabled.
    if not backup_settings.daily_backup:
        return

    # Timezone magic to make sure we select and compbine the CURRENT day, in the user's timezone.
    next_backup_timestamp = timezone.now().astimezone(
        settings.LOCAL_TIME_ZONE
    )
    next_backup_timestamp = timezone.datetime.combine(
        next_backup_timestamp, backup_settings.backup_time
    )
    next_backup_timestamp = timezone.make_aware(next_backup_timestamp, settings.LOCAL_TIME_ZONE)

    if backup_settings.latest_backup is not None \
            and backup_settings.latest_backup + timezone.timedelta(hours=24) > timezone.now() \
            and next_backup_timestamp > timezone.now():
        # Also skip when already having a backup, created within the last 24 hours and it's not time
        # to create a new one. This may result in unexpected behavior at the first backup creation.
        create()


def create():
    backup_folder = os.path.join(settings.BASE_DIR, settings.DSMR_BACKUP_DIRECTORY)
    print(backup_folder)
    pass

    BackupSettings.objects.update(latest_backup=timezone.now())


def sync():
    dsmr_backup.services.dropbox.sync()
