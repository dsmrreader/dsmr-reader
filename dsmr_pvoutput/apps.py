from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

import dsmr_backend.signals


class AppConfig(AppConfig):
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
