from datetime import time

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from solo.models import SingletonModel

from dsmr_backend.mixins import ModelUpdateMixin


class BackupSettings(ModelUpdateMixin, SingletonModel):
    """ Generic backup settings. """
    daily_backup = models.BooleanField(
        default=True,
        verbose_name=_('Backup daily'),
        help_text=_('Create a backup of your data daily. Stored locally, but can be exported using Dropbox.')
    )
    backup_time = models.TimeField(
        default=time(hour=2),
        verbose_name=_('Backup timestamp'),
        help_text=_(
            'Daily moment of creating the backup. You should prefer a nightly timestamp, as it '
            'might freeze or lock the application shortly during backup creation.'
        )
    )
    folder = models.CharField(
        max_length=512,
        default='backups/',
        verbose_name=_('Backup storage folder'),
        help_text=_(
            'The folder to store the backups in. The default location is "backups/". '
            'Please make sure that the "dsmr" user both has read and write access to the folder.'
        ),
    )
    latest_backup = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Latest backup'),
        help_text=_(
            'Timestamp of latest backup created. Automatically updated by application. Please note '
            'that the application will ignore the "backup_time" setting the first time used.'
        )
    )
    compression_level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(9)],
        verbose_name=_('Compression level'),
        help_text=_("The gzip compression level used. Level 9 = best, level 1 = fastest.")
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Backup configuration')


class DropboxSettings(ModelUpdateMixin, SingletonModel):
    """ Dropbox backup upload settings. """
    access_token = models.CharField(
        max_length=128,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Dropbox access token'),
    )
    latest_sync = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Latest sync'),
        help_text=_('Timestamp of latest sync with Dropbox. Automatically updated by application.')
    )
    next_sync = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Next sync'),
        help_text=_('Timestamp of next sync with Dropbox. Automatically updated by application.')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Dropbox configuration')


class EmailBackupSettings(ModelUpdateMixin, SingletonModel):
    """ Backup by email settings. """
    INTERVAL_NONE = None
    INTERVAL_DAILY = 1
    INTERVAL_WEEKLY = 7
    INTERVAL_BIWEEKLY = 14
    INTERVAL_MONTHLY = 28

    INTERVAL_CHOICES = (
        (INTERVAL_NONE, _('--- Disabled ---')),
        (INTERVAL_DAILY, _('Daily')),
        (INTERVAL_WEEKLY, _('Weekly')),
        (INTERVAL_BIWEEKLY, _('Every two weeks')),
        (INTERVAL_MONTHLY, _('Every four weeks')),
    )
    interval = models.IntegerField(
        null=True,
        blank=True,
        default=INTERVAL_NONE,
        choices=INTERVAL_CHOICES,
        verbose_name=_('Interval'),
        help_text=_('The frequency of sending backups per email')
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Email backup configuration')
