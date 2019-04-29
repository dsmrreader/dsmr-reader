from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import Group, User
from django.forms.widgets import TextInput
from django.utils import timezone
from django.contrib import admin
from django.db import models
from solo.admin import SingletonModelAdmin

from dsmr_backend.models.settings import BackendSettings, EmailSettings
from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.mixins import ReadOnlyAdminModel


# There is no global admin.py, so we'll just disable Group & User here.
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(BackendSettings)
class BackendSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['language'],
            }
        ),
    )


@admin.register(EmailSettings)
class EmailSettingsAdmin(SingletonModelAdmin):
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = (
        (
            None, {
                'fields': ['host', 'port', 'username', 'password', 'use_tls', 'use_ssl'],
                'description': _(
                    'Enter your outgoing email settings here, which DSMR-reader will use to send emails.'
                )
            }
        ),
    )


@admin.register(ScheduledProcess)
class ScheduledProcessAdmin(ReadOnlyAdminModel):
    list_display = ('name', 'planned', 'next_call_naturaltime')

    def next_call_naturaltime(self, obj):
        """ Fancy column to display time until next call, in relative time. """
        planned = obj.planned

        if planned < timezone.now():
            planned = timezone.now()

        return naturaltime(planned)

    next_call_naturaltime.short_description = _('Time until next call')
