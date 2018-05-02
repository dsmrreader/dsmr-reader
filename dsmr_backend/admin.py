from django.contrib import admin

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.auth.models import Group, User
from django.utils.translation import ugettext as _
from django.utils import timezone

from dsmr_backend.mixins import ReadOnlyAdminModel
from dsmr_backend.models import ScheduledCall


@admin.register(ScheduledCall)
class ScheduledCallAdmin(ReadOnlyAdminModel):
    list_display = ('module_path', 'name', 'next_call', 'next_call_naturaltime')

    def next_call_naturaltime(self, obj):
        """ Fancy column to display time until next call, in relative time. """
        next_call = obj.next_call

        if next_call < timezone.now():
            next_call = timezone.now()

        return naturaltime(next_call)

    next_call_naturaltime.short_description = _('Time until next call')


# Too bad there is no global admin.py, so we'll just disabled Group & User here.
admin.site.unregister(Group)
admin.site.unregister(User)
