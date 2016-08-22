import os

from django.utils import timezone
from django.conf import settings
from dropbox import Dropbox
from dropbox.exceptions import ApiError

from dsmr_backup.models.settings import DropboxSettings
import dsmr_backup.services.backup
from dropbox.files import UploadSessionCursor, CommitInfo


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

    retries = 3
    dbx = Dropbox(dropbox_settings.access_token)

    CHUNK_SIZE = 1 * 1024 * 1024  # In Bytes.

    with open(file_path, 'rb') as file_handle:
        result = dbx.files_upload_session_start(f='')

        # For some reason Dropbox want us to track this.
        session_cursor = UploadSessionCursor(session_id=result.session_id, offset=0)
        data = file_handle.read(CHUNK_SIZE)

        while data != b"":
            try:
                dbx.files_upload_session_append_v2(f=data, cursor=session_cursor)
            except ApiError as error:   # pragma: no cover
                retries -= 1  # pragma: no cover

                if retries == 0:  # pragma: no cover
                    raise IOError("Failed to upload to dropbox: {}".format(error))  # pragma: no cover

                continue  # Retry.

            session_cursor.offset += len(data)
            data = file_handle.read(CHUNK_SIZE)

    # This will commit the file and persist it in Dropbox.
    dbx.files_upload_session_finish(
        f='',
        cursor=session_cursor,
        commit=CommitInfo(
            path='/{}'.format(file_name),  # The slash indicates it's relative to the root of app folder.
            autorename=False
        )
    )
