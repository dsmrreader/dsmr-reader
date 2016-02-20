import subprocess
import shutil
import gzip
import os

from django.db import connection
from django.utils import timezone
from django.conf import settings
from django.utils import formats


from dsmr_backup.models.settings import BackupSettings
import dsmr_backup.services.dropbox


def check():
    """ Checks whether a new backup should be created. Creates one if needed as well. """
    backup_settings = BackupSettings.get_solo()

    # Skip when backups disabled.
    if not backup_settings.daily_backup:
        return

    # Timezone magic to make sure we select and combine the CURRENT day, in the user's timezone.
    next_backup_timestamp = timezone.now().astimezone(
        settings.LOCAL_TIME_ZONE
    )
    next_backup_timestamp = timezone.datetime.combine(
        next_backup_timestamp, backup_settings.backup_time
    )
    next_backup_timestamp = timezone.make_aware(next_backup_timestamp, settings.LOCAL_TIME_ZONE)

    if backup_settings.latest_backup is None or (
        backup_settings.latest_backup + timezone.timedelta(hours=24) < timezone.now() and
            next_backup_timestamp < timezone.now()
    ):
        # Create backup when: none created yet or the last one was over 24 hours ago and past
        # prefered daily backup creation time.
        create()


def get_backup_directory():
    """ Returns the path to the directory where all backups are stored locally. """
    return os.path.join(settings.BASE_DIR, '..', settings.DSMR_BACKUP_DIRECTORY)


def create():
    """ Creates a backup of the database. Optionally gzipped. """
    # Backup file with day name included, for weekly rotation.
    backup_file = os.path.join(get_backup_directory(), 'dsmrreader-{}-backup-{}.sql'.format(
        connection.vendor, formats.date_format(timezone.now().date(), 'l')
    ))

    # PostgreSQL backup.
    if connection.vendor == 'postgresql':
        backup_process = subprocess.Popen(
            [
                'pg_dump',
                '--host={}'.format(settings.DATABASES['default']['HOST']),
                '--user={}'.format(settings.DATABASES['default']['USER']),
                '--dbname={}'.format(settings.DATABASES['default']['NAME']),
            ], env={
                'PGPASSWORD': settings.DATABASES['default']['PASSWORD']
            },
            stdout=open(backup_file, 'w')
        )
    # MySQL backup.
    elif connection.vendor == 'mysql':
        backup_process = subprocess.Popen(
            [
                'mysqldump',
                '--compress',
                '--hex-blob',
                '--extended-insert',
                '--quick',
                '--host', settings.DATABASES['default']['HOST'],
                '--user', settings.DATABASES['default']['USER'],
                '--password={}'.format(settings.DATABASES['default']['PASSWORD']),
                settings.DATABASES['default']['NAME'],
            ],
            stdout=open(backup_file, 'w')
        )
    else:
        raise NotImplementedError('Unsupported backup backend: {}'.format(connection.vendor))

    backup_process.wait()
    backup_settings = BackupSettings.get_solo()

    if backup_settings.compress:
        compress(file_path=backup_file)

    backup_settings.latest_backup = timezone.now()
    backup_settings.save()


def compress(file_path, compresslevel=1):
    """ Compresses a file using (fast) gzip. Removes source file when compression succeeded. """
    file_path_gz = '{}.gz'.format(file_path)

    # Straight from the Python 3x docs.
    with open(file_path, 'rb') as f_in:
        with gzip.open(file_path_gz, 'wb', compresslevel=compresslevel) as f_out:
            shutil.copyfileobj(f_in, f_out)

    if os.stat(file_path_gz).st_size == 0:
        raise IOError('Failed to compress {}'.format(file_path))

    os.unlink(file_path)


def sync():
    """ Syncs all backups using cloud services. """
    dsmr_backup.services.dropbox.sync()
