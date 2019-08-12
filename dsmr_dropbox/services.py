import logging
import os

from django.utils.translation import ugettext_lazy as gettext
from django.utils import timezone
from django.conf import settings
import dropbox

from dsmr_backup.models.settings import DropboxSettings
from dsmr_dropbox.dropboxinc.dropbox_content_hasher import DropboxContentHasher
from dsmr_frontend.models.message import Notification
import dsmr_backup.services.backup


logger = logging.getLogger('commands')


def sync():
    dropbox_settings = DropboxSettings.get_solo()

    # Skip when either no token was entered.
    if not dropbox_settings.access_token:
        return

    if dropbox_settings.next_sync and dropbox_settings.next_sync > timezone.now():
        return

    backup_directory = dsmr_backup.services.backup.get_backup_directory()

    # Sync each file, recursively.
    for (root, dirs, filenames) in os.walk(backup_directory):
        for current_file in filenames:
            sync_file(
                dropbox_settings=dropbox_settings,
                local_root_dir=backup_directory,
                abs_file_path=os.path.abspath(os.path.join(root, current_file))
            )

    # Try again in a while.
    DropboxSettings.objects.update(
        latest_sync=timezone.now(),
        next_sync=timezone.now() + timezone.timedelta(
            hours=settings.DSMRREADER_DROPBOX_SYNC_INTERVAL
        )
    )


def sync_file(dropbox_settings, local_root_dir, abs_file_path):
    # The path we use in our Dropbox app folder.
    relative_file_path = abs_file_path.replace(local_root_dir, '')

    # Ignore empty files.
    if os.stat(abs_file_path).st_size == 0:
        return

    # Check whether the file is already at Dropbox, if so, check its hash.
    dbx = dropbox.Dropbox(dropbox_settings.access_token)

    try:
        dropbox_meta = dbx.files_get_metadata(relative_file_path)
    except dropbox.exceptions.ApiError as exception:
        error_message = str(exception.error)
        dropbox_meta = None

        # Unexpected.
        if 'not_found' not in error_message:
            return logger.error(' - Dropbox error: %s', error_message)

    # Calculate local hash and compare with remote. Ignore if the remote file is exactly the same.
    if dropbox_meta and calculate_content_hash(abs_file_path) == dropbox_meta.content_hash:
        return logger.debug(' - Dropbox content hash is the same, skipping: %s', relative_file_path)

    try:
        upload_chunked(
            dropbox_settings=dropbox_settings,
            local_file_path=abs_file_path,
            remote_file_path=relative_file_path
        )
    except dropbox.exceptions.DropboxException as exception:
        error_message = str(exception.error)
        logger.error(' - Dropbox error: %s', error_message)

        if 'insufficient_space' in error_message:
            Notification.objects.create(message=gettext(
                "[{}] Unable to upload files to Dropbox due to {}. "
                "Ignoring new files for the next {} hours...".format(
                    timezone.now(),
                    error_message,
                    settings.DSMRREADER_DROPBOX_ERROR_INTERVAL
                )
            ))
            DropboxSettings.objects.update(
                latest_sync=timezone.now(),
                next_sync=timezone.now() + timezone.timedelta(hours=settings.DSMRREADER_DROPBOX_ERROR_INTERVAL)
            )

        # Do not bother trying again.
        if 'invalid_access_token' in error_message:
            Notification.objects.create(message=gettext(
                "[{}] Unable to upload files to Dropbox due to {}. Removing credentials...".format(
                    timezone.now(),
                    error_message
                )
            ))
            DropboxSettings.objects.update(
                latest_sync=timezone.now(),
                next_sync=None,
                access_token=None
            )

        raise


def upload_chunked(dropbox_settings, local_file_path, remote_file_path):
    """ Uploads a file in chucks to Dropbox, allowing it to resume on (connection) failure. """
    logger.info(' - Syncing file with Dropbox: %s', remote_file_path)

    dbx = dropbox.Dropbox(dropbox_settings.access_token)
    write_mode = dropbox.files.WriteMode.overwrite

    file_handle = open(local_file_path, 'rb')
    file_size = os.path.getsize(local_file_path)

    # Many thanks to https://stackoverflow.com/documentation/dropbox-api/409/uploading-a-file/1927/uploading-a-file-usin
    # g-the-dropbox-python-sdk#t=201610181733061624381
    CHUNK_SIZE = 2 * 1024 * 1024

    # Small uploads should be transfers at one go.
    if file_size <= CHUNK_SIZE:
        dbx.files_upload(file_handle.read(), remote_file_path, mode=write_mode)

    # Large uploads can be sent in chunks, by creating a session allowing multiple separate uploads.
    else:
        upload_session_start_result = dbx.files_upload_session_start(file_handle.read(CHUNK_SIZE))

        cursor = dropbox.files.UploadSessionCursor(
            session_id=upload_session_start_result.session_id,
            offset=file_handle.tell()
        )
        commit = dropbox.files.CommitInfo(path=remote_file_path, mode=write_mode)

        # We keep sending the data in chunks, until we reach the last one, then we instruct Dropbox to finish the upload
        # by combining all the chunks sent previously.
        while file_handle.tell() < file_size:
            if (file_size - file_handle.tell()) <= CHUNK_SIZE:
                dbx.files_upload_session_finish(file_handle.read(CHUNK_SIZE), cursor, commit)
            else:
                dbx.files_upload_session_append(file_handle.read(CHUNK_SIZE), cursor.session_id, cursor.offset)
                cursor.offset = file_handle.tell()

    file_handle.close()


def calculate_content_hash(file_path):
    """ Calculates the Dropbox hash of a file: https://www.dropbox.com/developers/reference/content-hash """
    hasher = DropboxContentHasher()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(DropboxContentHasher.BLOCK_SIZE)
            if len(chunk) == 0:
                break
            hasher.update(chunk)

    return hasher.hexdigest()
