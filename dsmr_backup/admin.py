import pickle  # noqa: S403

from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.forms import TextInput
from django.utils import timezone
from django.contrib import admin, messages
from django.conf import settings
from django.db import models
from solo.admin import SingletonModelAdmin
import django.db.models.signals

from dsmr_backup.forms import BackupSettingsAdminForm
from .models.settings import BackupSettings, DropboxSettings, EmailBackupSettings
from dsmr_backend.models.settings import EmailSettings
from dsmr_backend.models.schedule import ScheduledProcess


@admin.register(BackupSettings)
class BackupSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_backup/backup_settings/change_form.html'
    form = BackupSettingsAdminForm
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = (
        (
            None, {
                'fields': ['daily_backup', 'backup_time'],
                'description': _(
                    'Detailed instructions for restoring a backup can be found here <a href="https://dsmr-reader.read'
                    'thedocs.io/nl/v5/how-to/database/postgresql-restore-backup.html">in documentation</a>.'
                )
            }
        ),
        (
            _('Advanced'), {
                'fields': ['folder', 'compression_level'],
            }
        ),
    )


@admin.register(DropboxSettings)
class DropboxSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_backup/dropbox_settings/change_form.html'
    readonly_fields = ('_settings_app_key', '_masked_refresh_token')
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = None  # See below.

    def get_fieldsets(self, request, obj=None):
        """ Method due to reverse_lazy() usage """
        return (
            (
                _('One-time set up with Dropbox Access Code'), {
                    'fields': ['one_time_authorization_code', '_settings_app_key', '_masked_refresh_token'],
                }
            ),
        )

    def save_model(self, request, obj, form, change):  # pragma: no cover
        """ Hook for finishing Dropbox app authorization flow."""
        if not obj.serialized_auth_flow or not obj.one_time_authorization_code:
            return super(DropboxSettingsAdmin, self).save_model(request, obj, form, change)

        auth_flow = pickle.loads(obj.serialized_auth_flow)  # noqa: S3-1

        try:
            oauth_result = auth_flow.finish(form.cleaned_data['one_time_authorization_code'])
        except Exception as e:
            messages.error(request, _('Dropbox app authorization failed: {}'.format(e)))
            return super(DropboxSettingsAdmin, self).save_model(request, obj, form, change)

        obj.serialized_auth_flow = None
        obj.refresh_token = oauth_result.refresh_token
        obj.one_time_authorization_code = None

        messages.success(request, _('Dropbox app authorization completed!'))
        super(DropboxSettingsAdmin, self).save_model(request, obj, form, change)

    def _settings_app_key(self, obj: DropboxSettings) -> str:  # pragma: no cover
        return settings.DSMRREADER_DROPBOX_APP_KEY
    _settings_app_key.short_description = _('Dropbox App Key')

    def _masked_refresh_token(self, obj: DropboxSettings) -> str:  # pragma: no cover
        return '✅' if obj.refresh_token else '❌'
    _masked_refresh_token.short_description = _('Dropbox refresh token')


@admin.register(EmailBackupSettings)
class EmailBackupSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_backup/email_backup_settings/change_form.html'
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = (
        (
            None, {
                'fields': ['interval'],
                'description': _(
                    'You can have DSMR-reader email you a backup every once in a while.'
                    '<br><br>Please note that the backup will <strong>ONLY contain day and hour statistics</strong>, '
                    'which are the most important data to preserve historically.'
                )
            }
        ),
    )

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update(dict(email_address=EmailSettings.get_solo().email_to))
        return super(EmailBackupSettingsAdmin, self).render_change_form(
            request, context, add, change, form_url, obj
        )

    def response_change(self, request, obj):
        ScheduledProcess.objects.filter(
            module=settings.DSMRREADER_MODULE_EMAIL_BACKUP
        ).update(planned=timezone.now())
        return super(EmailBackupSettingsAdmin, self).response_change(request, obj)


""" Hooks to toggle related scheduled process. """


@receiver(django.db.models.signals.post_save, sender=EmailBackupSettings)
def handle_email_backup_settings_update(sender, instance, **kwargs):
    ScheduledProcess.objects.filter(
        module=settings.DSMRREADER_MODULE_EMAIL_BACKUP
    ).update(active=instance.interval != EmailBackupSettings.INTERVAL_NONE)


@receiver(django.db.models.signals.post_save, sender=BackupSettings)
def handle_backup_settings_update(sender, instance, **kwargs):
    ScheduledProcess.objects.filter(
        module=settings.DSMRREADER_MODULE_DAILY_BACKUP
    ).update(
        planned=timezone.now(),
        active=instance.daily_backup
    )


@receiver(django.db.models.signals.post_save, sender=DropboxSettings)
def handle_dropbox_settings_update(sender, instance, **kwargs):
    ScheduledProcess.objects.filter(
        module=settings.DSMRREADER_MODULE_DROPBOX_EXPORT
    ).update(
        planned=timezone.now(),
        active=bool(instance.refresh_token)
    )
