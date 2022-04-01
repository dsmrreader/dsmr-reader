import subprocess
import logging
import shutil
import gzip
import os
from typing import Iterable, NoReturn

from django.utils.translation import gettext as _
from django.db import connection
from django.utils import timezone
from django.conf import settings
from django.utils import formats

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_stats.models.statistics import DayStatistics
from dsmr_backup.models.settings import BackupSettings
import dsmr_frontend.services


logger = logging.getLogger('dsmrreader')


def run(scheduled_process: ScheduledProcess) -> None:
    """ Checks whether a new backup should be created. Creates one if needed as well. """

    # Create a partial, minimal backup first. Since it will grow and take disk space, only create one weekly.
    today = timezone.localtime(timezone.now()).date()

    if today.isoweekday() == 1:
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

    # Schedule tomorrow, for the time specified.
    backup_settings = BackupSettings.get_solo()
    next_backup_timestamp = timezone.now() + timezone.timedelta(days=1)
    next_backup_timestamp = timezone.localtime(next_backup_timestamp)

    next_backup_timestamp = next_backup_timestamp.replace(
        hour=backup_settings.backup_time.hour,
        minute=backup_settings.backup_time.minute,
        second=0,
        microsecond=0
    )

    scheduled_process.reschedule(next_backup_timestamp)


def get_backup_directory(backup_directory=None) -> str:
    """ Returns the path to the directory where all backups are stored locally. """
    if not backup_directory:
        backup_directory = BackupSettings.get_solo().folder

    if backup_directory.startswith('/'):
        return os.path.abspath(backup_directory)

    return os.path.abspath(os.path.join(settings.BASE_DIR, '..', backup_directory))


def create_full(folder: str) -> str:
    """ Creates a backup of the database. Optionally gzipped. """
    if not os.path.exists(folder):
        logger.info(' - Creating non-existing backup folder: %s', folder)
        os.makedirs(folder)

    # Backup file with day name included, for weekly rotation.
    backup_file = os.path.join(folder, '{}-{}-backup-{}.sql'.format(
        settings.DSMRREADER_BACKUP_NAME_PREFIX,
        connection.vendor,
        formats.date_format(timezone.now().date(), 'l')
    ))

    logger.info(' - Creating new full backup: %s', backup_file)
    db_settings = settings.DATABASES['default']

    # PostgreSQL backup.
    if connection.vendor == 'postgresql':  # pragma: no cover
        command = [
            settings.DSMRREADER_BACKUP_PG_DUMP,
            '--host={}'.format(db_settings['HOST']),
            '--port={}'.format(db_settings['PORT']),
            '--user={}'.format(db_settings['USER']),
            db_settings['NAME'],
        ]
        backup_process = subprocess.Popen(command, env={
            **os.environ,
            'PGPASSWORD': db_settings['PASSWORD']
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
            '--host', db_settings['HOST'],
            '--user', db_settings['USER'],
            '--password={}'.format(db_settings['PASSWORD']),
            db_settings['NAME'],
        ]
        backup_process = subprocess.Popen(command, stdout=open(backup_file, 'w'))  # pragma: no cover
    # SQLite backup.
    elif connection.vendor == 'sqlite':  # pragma: no cover
        command = [
            settings.DSMRREADER_BACKUP_SQLITE,
            db_settings['NAME'],
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
    return backup_file


def create_partial(folder: str, models_to_backup: Iterable) -> str:  # pragma: no cover
    """ Creates a backup of the database, but only containing a subset specified by models."""
    if not os.path.exists(folder):
        logger.info(' - Creating non-existing backup folder: %s', folder)
        os.makedirs(folder)

    backup_file = os.path.join(folder, '{}-{}-partial-backup-{}.sql'.format(
        settings.DSMRREADER_BACKUP_NAME_PREFIX,
        connection.vendor,
        formats.date_format(timezone.now().date(), 'Y-m-d')
    ))

    logger.info(' - Creating new partial backup: %s', backup_file)
    db_settings = settings.DATABASES['default']

    if connection.vendor == 'postgresql':  # pragma: no cover
        command = [
            settings.DSMRREADER_BACKUP_PG_DUMP,
            db_settings['NAME'],
            '--data-only',
            '--host={}'.format(db_settings['HOST']),
            '--port={}'.format(db_settings['PORT']),
            '--user={}'.format(db_settings['USER']),
        ] + [
            '--table={}'.format(x._meta.db_table) for x in models_to_backup
        ]
        backup_process = subprocess.Popen(
            command,
            env={
                **os.environ,
                'PGPASSWORD': db_settings['PASSWORD']
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
            '--host', db_settings['HOST'],
            '--user', db_settings['USER'],
            '--password={}'.format(db_settings['PASSWORD']),
            db_settings['NAME'],
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


def on_backup_failed(process_handle) -> NoReturn:
    """ Triggered when backup creation fails. """
    error_message = process_handle.stderr.read()
    logger.critical(' - Unexpected exit code (%s) for backup: %s', process_handle.returncode, error_message)

    dsmr_frontend.services.display_dashboard_message(message=_(
        'Backup creation failed, please check the dsmr_backend logfile.'
    ))

    raise IOError(error_message)


def compress(file_path: str) -> str:
    """ Compresses a file using (fast) gzip. Removes source file when compression succeeded. """
    compression_level = BackupSettings.get_solo().compression_level

    file_path_gz = '{}.gz'.format(file_path)

    # Straight from the Python 3x docs.
    with open(file_path, 'rb') as f_in:
        with gzip.open(file_path_gz, 'wb', compresslevel=compression_level) as f_out:
            shutil.copyfileobj(f_in, f_out)

    os.unlink(file_path)
    return file_path_gz
