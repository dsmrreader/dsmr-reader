from django.contrib import admin
from django.forms import TextInput
from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from .models.settings import BackupSettings, DropboxSettings


@admin.register(BackupSettings)
class BackupSettingsAdmin(SingletonModelAdmin):
    readonly_fields = ('latest_backup', )
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
                'fields': ['compress'],
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
