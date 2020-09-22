from django.apps import AppConfig
from django.conf import settings
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

    offset = timezone.now() - timezone.timedelta(
        minutes=settings.DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES
    )

    if pvoutput_settings.next_export > offset:
        return

    return MonitoringStatusIssue(
        __name__,
        _('Waiting for the next PVOutput export to be executed'),
        pvoutput_settings.next_export
    )
