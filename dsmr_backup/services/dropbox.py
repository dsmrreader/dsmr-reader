import os

from django.utils import timezone
from django.conf import settings
from dropbox.client import DropboxClient
from dropbox import rest

from dsmr_backup.models.settings import DropboxSettings
import dsmr_backup.services.backup


def sync():
    dropbox_settings = DropboxSettings.get_solo()

    # Skip when either no token was entered.
    if not dropbox_settings.access_token:
        return

    #  Or when we already synced within the last hour.
    next_sync_interval = None

    if dropbox_settings.latest_sync:
        next_sync_interval = dropbox_settings.latest_sync + timezone.timedelta(
            hours=settings.DSMR_DROPBOX_SYNC_INTERVAL
        )

    if next_sync_interval and timezone.now() < next_sync_interval:
        return

    backup_directory = dsmr_backup.services.backup.get_backup_directory()

    # Just check for modified files since the last sync.
    for (_, _, filenames) in os.walk(backup_directory):
        for current_file in filenames:
            current_file_path = os.path.join(backup_directory, current_file)
            file_stats = os.stat(current_file_path)

            # Ignore empty files.
            if file_stats.st_size == 0:
                continue

            last_modified = timezone.datetime.fromtimestamp(file_stats.st_mtime)
            last_modified = timezone.make_aware(last_modified)

            # Ignore when file was not altered since last sync.
            if dropbox_settings.latest_sync and last_modified < dropbox_settings.latest_sync:
                continue

            upload_chunked(file_path=current_file_path)

    DropboxSettings.objects.update(latest_sync=timezone.now())


def upload_chunked(file_path):
    """ Uploads a file in chucks to Dropbox, allowing it to resume on (connection) failure. """
    dropbox_settings = DropboxSettings.get_solo()
    file_name = os.path.split(file_path)[-1]

    # From Dropbox docs.
    retries = 3
    client = DropboxClient(dropbox_settings.access_token)

    size = os.stat(file_path).st_size
    file_handle = open(file_path, 'rb')

    uploader = client.get_chunked_uploader(file_handle, size)

    while uploader.offset < size:
        try:
            uploader.upload_chunked(chunk_size=1 * 1024 * 1024)
        except rest.ErrorResponse:
            retries -= 1

            if retries == 0:
                raise IOError("Failed to upload to dropbox")

    # This will commit the file and persist it in Dropbox. Due to rotating backups we MUST override.
    uploader.finish(file_name, overwrite=True)
