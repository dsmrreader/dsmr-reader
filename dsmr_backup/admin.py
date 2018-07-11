from django.contrib import admin
from django.forms import TextInput
from django.db import models
from django.utils.translation import ugettext_lazy as _
from solo.admin import SingletonModelAdmin

from .models.settings import BackupSettings, DropboxSettings


@admin.register(BackupSettings)
class BackupSettingsAdmin(SingletonModelAdmin):
    list_display = ('daily_backup', 'compress', 'backup_time')
    readonly_fields = ('latest_backup', )
    fieldsets = (
        (
            None, {
                'fields': ['daily_backup', 'compress', 'backup_time', 'latest_backup'],
                'description': _(
                    'Detailed instructions for restoring a backup can be found here: <a href="https://dsmr-reader.readt'
                    'hedocs.io/nl/latest/faq.html#how-do-i-restore-a-database-backup">FAQ in documentation</a>'
                )
            }
        ),
    )


@admin.register(DropboxSettings)
class DropboxSettingsAdmin(SingletonModelAdmin):
    list_display = ('access_token', 'latest_sync')
    readonly_fields = ('latest_sync', 'next_sync')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = (
        (
            None, {
                'fields': ['access_token', 'latest_sync', 'next_sync'],
                'description': _(
                    'Detailed instructions for configuring Dropbox can be found here: <a href="https://dsmr-reader.read'
                    'thedocs.io/nl/latest/faq.html#dropbox-automated-backup-sync">FAQ in documentation</a>'
                )
            }
        ),
    )
