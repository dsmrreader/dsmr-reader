import subprocess
import logging
import shutil
import gzip
import os

from django.utils.translation import ugettext as _
from django.db import connection
from django.utils import timezone
from django.conf import settings
from django.utils import formats

from dsmr_stats.models.statistics import DayStatistics
from dsmr_backup.models.settings import BackupSettings
import dsmr_dropbox.services
import dsmr_frontend.services


logger = logging.getLogger('commands')


def check():
    """ Checks whether a new backup should be created. Creates one if needed as well. """
    backup_settings = BackupSettings.get_solo()

    # Skip when backups disabled.
    if not backup_settings.daily_backup:
        return

    # Postpone when we already created a backup today.
    if backup_settings.latest_backup and backup_settings.latest_backup.date() == timezone.now().date():
        return

    # Timezone magic to make sure we select and combine the CURRENT day, in the user's timezone.
    next_backup_timestamp = timezone.make_aware(timezone.datetime.combine(
        timezone.localtime(timezone.now()), backup_settings.backup_time
    ))

    if backup_settings.latest_backup and timezone.now() < next_backup_timestamp:
        # Postpone when the user's backup time preference has not been passed yet.
        return

    # Create a partial, minimal backup first.
    today = timezone.localtime(timezone.now()).date()
    create_partial(
        folder=os.path.join(
            get_backup_directory(),
            'archive',
            formats.date_format(today, 'Y'),
            formats.date_format(today, 'm')
        ),
        models_to_backup=(DayStatistics, )
    )

    # Now create full.
    create_full(folder=get_backup_directory())

    backup_settings = BackupSettings.get_solo()
    backup_settings.latest_backup = timezone.now()
    backup_settings.save()


def get_backup_directory(backup_directory=None):
    """ Returns the path to the directory where all backups are stored locally. """
    if not backup_directory:
        backup_directory = BackupSettings.get_solo().folder

    if backup_directory.startswith('/'):
        return os.path.abspath(backup_directory)

    return os.path.abspath(os.path.join(settings.BASE_DIR, '..', backup_directory))


def create_full(folder):
    """ Creates a backup of the database. Optionally gzipped. """
    if not os.path.exists(folder):
        logger.info(' - Creating non-existing backup folder: %s', folder)
        os.makedirs(folder)

    # Backup file with day name included, for weekly rotation.
    backup_file = os.path.join(folder, 'dsmrreader-{}-backup-{}.sql'.format(
        connection.vendor, formats.date_format(timezone.now().date(), 'l')
    ))

    logger.info(' - Creating new full backup: %s', backup_file)

    # PostgreSQL backup.
    if connection.vendor == 'postgresql':  # pragma: no cover
        command = [
            settings.DSMRREADER_BACKUP_PG_DUMP,
            '--host={}'.format(settings.DATABASES['default']['HOST']),
            '--user={}'.format(settings.DATABASES['default']['USER']),
            settings.DATABASES['default']['NAME'],
        ]
        backup_process = subprocess.Popen(command, env={
                'PGPASSWORD': settings.DATABASES['default']['PASSWORD']
            },
            stdout=open(backup_file, 'w')  # pragma: no cover
        )
    # MySQL backup.
    elif connection.vendor == 'mysql':  # pragma: no cover
        command = [
            settings.DSMRREADER_BACKUP_MYSQLDUMP,
            '--compress',
            '--hex-blob',
            '--extended-insert',
            '--quick',
            '--host', settings.DATABASES['default']['HOST'],
            '--user', settings.DATABASES['default']['USER'],
            '--password={}'.format(settings.DATABASES['default']['PASSWORD']),
            settings.DATABASES['default']['NAME'],
        ]
        backup_process = subprocess.Popen(command, stdout=open(backup_file, 'w'))  # pragma: no cover
    # SQLite backup.
    elif connection.vendor == 'sqlite':  # pragma: no cover
        command = [
            settings.DSMRREADER_BACKUP_SQLITE,
            settings.DATABASES['default']['NAME'],
            '.dump',
        ]
        backup_process = subprocess.Popen(
            command,
            stdout=open(backup_file, 'w'),
            stderr=subprocess.PIPE
        )  # pragma: no cover
    else:
        raise NotImplementedError('Unsupported backup backend: {}'.format(connection.vendor))  # pragma: no cover

    backup_process.wait()
    logger.debug(' - Backup exit code: %s', backup_process.returncode)

    if backup_process.returncode != 0:
        on_backup_failed(process_handle=backup_process)

    backup_file = compress(file_path=backup_file)
    logger.info(' - Created and compressed full backup: %s', backup_file)


def create_partial(folder, models_to_backup):  # pragma: no cover
    """ Creates a backup of the database, but only containing a subset specified by models."""
    if not os.path.exists(folder):
        logger.info(' - Creating non-existing backup folder: %s', folder)
        os.makedirs(folder)

    backup_file = os.path.join(folder, 'dsmrreader-{}-partial-backup-{}.sql'.format(
        connection.vendor, formats.date_format(timezone.now().date(), 'Y-m-d')
    ))

    logger.info(' - Creating new partial backup: %s', backup_file)

    if connection.vendor == 'postgresql':  # pragma: no cover
        command = [
            settings.DSMRREADER_BACKUP_PG_DUMP,
            settings.DATABASES['default']['NAME'],
            '--data-only',
            '--host={}'.format(settings.DATABASES['default']['HOST']),
            '--user={}'.format(settings.DATABASES['default']['USER']),
        ] + [
            '--table={}'.format(x._meta.db_table) for x in models_to_backup
        ]
        backup_process = subprocess.Popen(
            command,
            env={
                'PGPASSWORD': settings.DATABASES['default']['PASSWORD']
            },
            stdout=open(backup_file, 'w'),
            stderr=subprocess.PIPE
        )
    # MySQL backup.
    elif connection.vendor == 'mysql':  # pragma: no cover
        command = [
            settings.DSMRREADER_BACKUP_MYSQLDUMP,
            '--compress',
            '--compact',
            '--hex-blob',
            '--extended-insert',
            '--quick',
            '--host', settings.DATABASES['default']['HOST'],
            '--user', settings.DATABASES['default']['USER'],
            '--password={}'.format(settings.DATABASES['default']['PASSWORD']),
            settings.DATABASES['default']['NAME'],
        ] + [
            x._meta.db_table for x in models_to_backup
        ]
        backup_process = subprocess.Popen(command, stdout=open(backup_file, 'w'))  # pragma: no cover
    else:
        raise NotImplementedError('Unsupported backup backend: {}'.format(connection.vendor))

    backup_process.wait()
    logger.debug(' - Backup exit code: %s', backup_process.returncode)

    if backup_process.returncode != 0:
        on_backup_failed(process_handle=backup_process)

    backup_file = compress(file_path=backup_file)
    logger.info(' - Created and compressed statistics backup: %s', backup_file)
    return backup_file


def on_backup_failed(process_handle):
    """ Triggered when backup creation fails. """
    error_message = process_handle.stderr.read()
    logger.critical(' - Unexpected exit code (%s) for backup: %s', process_handle.returncode, error_message)

    dsmr_frontend.services.display_dashboard_message(message=_(
        'Backup creation failed, please check the dsmr_backend logfile.'
    ))

    raise IOError(error_message)


def compress(file_path, compresslevel=1):
    """ Compresses a file using (fast) gzip. Removes source file when compression succeeded. """
    file_path_gz = '{}.gz'.format(file_path)

    # Straight from the Python 3x docs.
    with open(file_path, 'rb') as f_in:
        with gzip.open(file_path_gz, 'wb', compresslevel=compresslevel) as f_out:
            shutil.copyfileobj(f_in, f_out)

    os.unlink(file_path)
    return file_path_gz


def sync():
    """ Syncs backup folder with remote storage. """
    dsmr_dropbox.services.sync()
