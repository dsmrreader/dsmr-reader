from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

import dsmr_backend.signals


class AppConfig(AppConfig):
    name = 'dsmr_datalogger'
    verbose_name = _('Datalogger')

    def ready(self):
        dsmr_backend.signals.backend_called.connect(
            receiver=self._on_backend_called_signal,
            dispatch_uid=self.__class__
        )

    def _on_backend_called_signal(self, sender, **kwargs):
        # Import below prevents an AppRegistryNotReady error on Django init.
        import dsmr_datalogger.services
        dsmr_datalogger.services.apply_data_retention()
