from django.apps import AppConfig
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backend.signals import request_status
import dsmr_backend.signals


class PvoutputAppConfig(AppConfig):
    name = 'dsmr_pvoutput'
    verbose_name = _('PVOutput')

    def ready(self):
        dsmr_backend.signals.backend_called.connect(
            receiver=self._on_backend_called_signal,
            dispatch_uid=self.__class__
        )

    def _on_backend_called_signal(self, sender, **kwargs):
        # Import below prevents an AppRegistryNotReady error on Django init.
        import dsmr_pvoutput.services
        dsmr_pvoutput.services.export()


@receiver(request_status)
def check_pvoutput_sync(**kwargs):
    from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings
    pvoutput_settings = PVOutputAddStatusSettings.get_solo()

    if not pvoutput_settings.export:
        return

    offset = timezone.now() - timezone.timedelta(hours=1)

    if pvoutput_settings.next_export > offset:
        return

    return MonitoringStatusIssue(
        __name__,
        'PVOutput sync took too long',
        pvoutput_settings.next_export
    )
