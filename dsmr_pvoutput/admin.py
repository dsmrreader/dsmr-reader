from django.conf import settings
from django.contrib import admin
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin
import django.db.models.signals

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_pvoutput.models.settings import PVOutputAPISettings, PVOutputAddStatusSettings


@admin.register(PVOutputAPISettings)
class PVOutputAPISettingsAdmin(SingletonModelAdmin):
    pass


@admin.register(PVOutputAddStatusSettings)
class PVOutputAddStatusSettingsAdmin(SingletonModelAdmin):
    fieldsets = (
        (
            None, {
                'fields': ['export', 'upload_interval', 'upload_delay'],
                'description': _(
                    'Implements the following API call: '
                    '<a href="https://pvoutput.org/help.html#api-addstatus" target="_blank">Add Status Service</a>'
                )
            }
        ),
        (
            _('PVOutput Donators'), {
                'fields': ['processing_delay'],
                'description': _(
                    'This feature is ONLY available when you have a DONATOR account for PVOutput.org. '
                    'For more information see: '
                    '<a href="https://pvoutput.org/donate.jsp" target="_blank">Donating to PVOutput</a> '
                    ' and <a href="https://pvoutput.org/help.html#donations" target="_blank">Bonus Features</a>.'
                )
            }
        ),
    )


""" Hooks to toggle related scheduled process. """


@receiver(django.db.models.signals.post_save, sender=PVOutputAPISettings)
def handle_pvoutput_api_settings_update(sender, instance, **kwargs):
    _on_pvoutput_setting_update()


@receiver(django.db.models.signals.post_save, sender=PVOutputAddStatusSettings)
def handle_pvoutput_add_status_settings_update(sender, instance, **kwargs):
    _on_pvoutput_setting_update()


def _on_pvoutput_setting_update():
    api_settings = PVOutputAPISettings.get_solo()
    add_status_settings = PVOutputAddStatusSettings.get_solo()

    ScheduledProcess.objects.filter(
        module=settings.DSMRREADER_MODULE_PVOUTPUT_EXPORT
    ).update(
        planned=timezone.now(),
        active=all([
            api_settings.auth_token,
            api_settings.system_identifier,
            add_status_settings.export
        ])
    )
