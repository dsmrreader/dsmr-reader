import os

from django.utils import timezone
from django.conf import settings
import dropbox

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
            hours=settings.DSMRREADER_DROPBOX_SYNC_INTERVAL
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
    # For backend logging in Supervisor.
    print(' - Uploading file to Dropbox: {}.'.format(file_path))

    dropbox_settings = DropboxSettings.get_solo()
    file_name = os.path.split(file_path)[-1]
    dest_path = '/{}'.format(file_name)  # The slash indicates it's relative to the root of app folder.

    dbx = dropbox.Dropbox(dropbox_settings.access_token)
    write_mode = dropbox.files.WriteMode.overwrite

    file_handle = open(file_path, 'rb')
    file_size = os.path.getsize(file_path)

    # Many thanks to https://stackoverflow.com/documentation/dropbox-api/409/uploading-a-file/1927/uploading-a-file-usin
    # g-the-dropbox-python-sdk#t=201610181733061624381
    CHUNK_SIZE = 2 * 1024 * 1024

    # Small uploads should be transfers at one go.
    if file_size <= CHUNK_SIZE:
        dbx.files_upload(file_handle.read(), dest_path, mode=write_mode)

    # Large uploads can be sent in chunks, by creating a session allowing multiple separate uploads.
    else:
        upload_session_start_result = dbx.files_upload_session_start(file_handle.read(CHUNK_SIZE))

        cursor = dropbox.files.UploadSessionCursor(
            session_id=upload_session_start_result.session_id,
            offset=file_handle.tell()
        )
        commit = dropbox.files.CommitInfo(path=dest_path, mode=write_mode)

        # We keep sending the data in chunks, until we reach the last one, then we instruct Dropbox to finish the upload
        # by combining all the chunks sent previously.
        while file_handle.tell() < file_size:
            if (file_size - file_handle.tell()) <= CHUNK_SIZE:
                dbx.files_upload_session_finish(file_handle.read(CHUNK_SIZE), cursor, commit)
            else:
                dbx.files_upload_session_append(file_handle.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                cursor.offset = file_handle.tell()

    file_handle.close()
