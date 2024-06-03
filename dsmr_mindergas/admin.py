from django.conf import settings
from django.contrib import admin
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from solo.admin import SingletonModelAdmin
import django.db.models.signals

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_mindergas.models.settings import MinderGasSettings


@admin.register(MinderGasSettings)
class MinderGasSettingsAdmin(SingletonModelAdmin):
    change_form_template = "dsmr_mindergas/mindergas_settings/change_form.html"
    fieldsets = (
        (
            None,
            {
                "fields": ["export", "auth_token"],
                "description": _(
                    'Detailed instructions for configuring MinderGas.nl can be found here: <a href="https://dsmr-reader'
                    '.readthedocs.io/nl/v5/how-to/admin/mindergas.html">Documentation</a>'
                ),
            },
        ),
    )


@receiver(django.db.models.signals.post_save, sender=MinderGasSettings)
def handle_mindergas_settings_update(sender, instance, **kwargs):
    """Hook to toggle related scheduled process."""
    ScheduledProcess.objects.filter(
        module=settings.DSMRREADER_MODULE_MINDERGAS_EXPORT
    ).update(active=instance.export)
