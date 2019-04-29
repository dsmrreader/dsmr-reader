from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.forms import TextInput
from django.db import models
from solo.admin import SingletonModelAdmin

from .models.settings import BackupSettings, DropboxSettings, EmailBackupSettings


@admin.register(BackupSettings)
class BackupSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('latest_backup', )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = (
        (
            None, {
                'fields': ['daily_backup', 'backup_time'],
                'description': _(
                    'Detailed instructions for restoring a backup can be found here: <a href="https://dsmr-reader.readt'
                    'hedocs.io/nl/latest/faq.html#how-do-i-restore-a-database-backup">FAQ in documentation</a>'
                )
            }
        ),
        (
            _('Advanced'), {
                'fields': ['folder', 'compress'],
            }
        ),
        (
            _('Automatic fields'), {
                'fields': ['latest_backup']
            }
        ),
    )


@admin.register(DropboxSettings)
class DropboxSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('latest_sync', 'next_sync')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = (
        (
            None, {
                'fields': ['access_token'],
                'description': _(
                    'Detailed instructions for configuring Dropbox can be found here: <a href="https://dsmr-reader.read'
                    'thedocs.io/nl/latest/admin/backup_dropbox.html">Documentation</a>'
                )
            }
        ),
        (
            _('Automatic fields'), {
                'fields': ['latest_sync', 'next_sync']
            }
        ),
    )


@admin.register(EmailBackupSettings)
class EmailBackupSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('latest_sync', 'next_sync')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = (
        (
            None, {
                'fields': ['email_to', 'interval'],
                'description': _(
                    'You can have DSMR-reader email you a backup every once in a while. Please note that the backup '
                    'will ONLY contain day and hour statistics, which are the most important data to preserve '
                    'historically.'
                )
            }
        ),
        (
            _('Automatic fields'), {
                'fields': ['latest_sync', 'next_sync']
            }
        ),
    )
