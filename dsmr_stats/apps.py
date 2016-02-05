from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

import dsmr_backend.signals


class AppConfig(AppConfig):
    name = 'dsmr_stats'
    verbose_name = _('Statistics')

    def ready(self):
        dsmr_backend.signals.backend_called.connect(
            receiver=self._on_backend_called_signal,
            dispatch_uid=self.__class__.__name__
        )

    def _on_backend_called_signal(self, sender, **kwargs):
        # Import below prevents an AppRegistryNotReady error on Django init.
        import dsmr_stats.services
        dsmr_stats.services.create_daily_statistics(day)
