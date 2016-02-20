import os

from django.utils import timezone
from django.conf import settings
from dropbox.client import DropboxClient
from dropbox import rest

from dsmr_backup.models.settings import DropboxSettings


def sync():
    dropbox_settings = DropboxSettings.get_solo()

    # Skip when either no token was entered or we already synced an hour ago.
    if not dropbox_settings.access_token:
        return

    if timezone.now() < dropbox_settings.latest_sync + timezone.timedelta(hour=1):
        return

#     backup_folder = os.path.join(settings.BASE_DIR, settings.DSMR_BACKUP_DIRECTORY)
#     print(backup_folder)
#     raise
#
#     FILE = "@TODO"
#     client = DropboxClient(dropbox_settings.access_token)
#
#     size = os.stat(FILE).st_size
#     bigFile = open(FILE, 'rb')
#
#     uploader = client.get_chunked_uploader(bigFile, size)
#     print("uploading: ", size)
#     while uploader.offset < size:
#         try:
#             upload = uploader.upload_chunked(chunk_size=1 * 1024 * 1024)
#             print('upload', upload)
#         except rest.ErrorResponse as e:
#             print(e)
#             # perform error handling and retry logic
#     uploader.finish('@TODO')

    DropboxSettings.objects.update(latest_sync=timezone.now())
