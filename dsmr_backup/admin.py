from django.contrib import admin
from django.forms import TextInput
from django.db import models
from solo.admin import SingletonModelAdmin

from .models.settings import BackupSettings, DropboxSettings


@admin.register(BackupSettings)
class BackupSettingsAdmin(SingletonModelAdmin):
    list_display = ('daily_backup', 'compress', 'backup_time')
    readonly_fields = ('latest_backup', )


@admin.register(DropboxSettings)
class DropboxSettingsAdmin(SingletonModelAdmin):
    list_display = ('access_token', )
    readonly_fields = ('latest_sync', )
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
