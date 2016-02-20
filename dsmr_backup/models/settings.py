from datetime import time

from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.models import SingletonModel


class BackupSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    daily_backup = models.BooleanField(
        default=True,
        verbose_name=_('Backup daily'),
        help_text=_(
            'Create a backup of your data daily. Stored locally, but can be exported using Dropbox.'
        )
    )
    compress = models.BooleanField(
        default=True,
        verbose_name=_('Compress'),
        help_text=_(
            'Create backups in compressed (gzip) format, saving a significant amount of disk space.'
        )
    )
    backup_time = models.TimeField(
        default=time(hour=2),
        verbose_name=_('Backup timestamp'),
        help_text=_(
            'Daily moment of creating the backup. You should prefer a nightly timestamp, as it '
            'might freeze or lock the application shortly during backup creation.'
        )
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

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Backup configuration')


class DropboxSettings(SingletonModel):
    """ Singleton model restricted by django-solo plugin. Settings for this application only. """
    access_token = models.CharField(
        max_length=128,
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Dropbox access token'),
        help_text=_(
            'The access token for your Dropbox account. You should register an App for your own '
            'Dropbox account ({}). Please select "Permission type" named "App folder" to restrict '
            'unneeded access. Backups will be synced to a dedicated folder in your account. After '
            'creating your App you should be able to generate an "Access token" and enter it here. '
            'See {} for more information.'.format(
                'https://www.dropbox.com/developers/apps',
                'https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own'
                '-account/'
            )
        )
    )

    latest_sync = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        verbose_name=_('Latest sync'),
        help_text=_(
            'Timestamp of latest sync with Dropbox. Automatically updated by application.'
        )
    )

    def __str__(self):
        return self._meta.verbose_name.title()

    class Meta:
        default_permissions = tuple()
        verbose_name = _('Dropbox configuration')
