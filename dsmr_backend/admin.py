from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _
from django.http.response import HttpResponseRedirect
from django.contrib.auth.models import Group, User
from django.utils import timezone, translation
from django.forms.widgets import TextInput
from django.contrib import admin
from django.db import models
from solo.admin import SingletonModelAdmin
import django.db.models.signals

from dsmr_backend.models.settings import BackendSettings, EmailSettings
from dsmr_backend.models.schedule import ScheduledProcess
import dsmr_backend.services.email
import logging


# There is no global admin.py, so we'll just disable Group & User here.
admin.site.unregister(Group)
admin.site.unregister(User)


@admin.register(BackendSettings)
class BackendSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['language', 'automatic_update_checker'],
            }
        ),
    )


@receiver(django.db.models.signals.post_save, sender=BackendSettings)
def handle_backend_settings_update(sender, instance, **kwargs):
    """ Hook to toggle related scheduled process. """
    ScheduledProcess.objects.filter(
        module=settings.DSMRREADER_MODULE_AUTO_UPDATE_CHECKER
    ).update(active=instance.automatic_update_checker)


@admin.register(EmailSettings)
class EmailSettingsAdmin(SingletonModelAdmin):
    change_form_template = 'dsmr_backend/email_settings/change_form.html'

    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '64'})},
    }
    fieldsets = (
        (
            None, {
                'fields': ['email_to'],
            }
        ),
        (
            _('Advanced'), {
                'fields': ['host', 'port', 'username', 'password', 'use_tls', 'use_ssl'],
                'description': _(
                    'Enter your outgoing email settings here, which DSMR-reader will use to send emails. '
                    '<br><br>Do you have GMail? Enter host <strong>aspmx.l.google.com</strong>, '
                    'port <strong>25</strong> and use <strong>TLS</strong>. '
                    'Do not enter any username of password and enter your GMail address as "Email to" above.'
                )
            }
        ),
    )

    def response_change(self, request, obj):
        if 'send_test_email' not in request.POST.keys():
            return super(EmailSettingsAdmin, self).response_change(request, obj)

        email_settings = EmailSettings.get_solo()

        with translation.override(language=BackendSettings.get_solo().language):
            subject = _('DSMR-reader email test')
            body = _('Test for your email settings.')

        try:
            dsmr_backend.services.email.send(
                email_settings.email_to,
                subject=subject,
                body=body
            )
        except Exception as error:
            self.message_user(request, _('Failed to send test email: {}'.format(error)), level=logging.ERROR)
            return HttpResponseRedirect('.')

        self.message_user(request, _('Email sent succesfully, please check your email inbox (and spam folder).'))
        return HttpResponseRedirect('.')


@admin.register(ScheduledProcess)
class ScheduledProcessAdmin(admin.ModelAdmin):
    list_display = ('active', 'name', 'planned', 'next_call_naturaltime')
    readonly_fields = ('name', 'module', 'active')
    list_display_links = ('name', 'planned')
    actions = None

    fieldsets = (
        (
            _('Internals'), {
                'fields': ['name', 'module', 'active'],
            }
        ),
        (
            ('Next call'), {
                'fields': ['planned'],
                'description': _(
                    _('Reschedule a process here. Do not modify unless you know why to change it.')
                )
            }
        ),
    )

    def next_call_naturaltime(self, obj):
        """ Fancy column to display time until next call, in relative time. """
        planned = obj.planned

        if planned < timezone.now():
            planned = timezone.now()

        return naturaltime(planned)

    next_call_naturaltime.short_description = _('Time until next call')

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
