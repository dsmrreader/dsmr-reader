from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

import dsmr_backend.signals


class AppConfig(AppConfig):
    name = 'dsmr_backup'
    verbose_name = _('Backup')

    def ready(self):
        dsmr_backend.signals.backend_called.connect(
            receiver=self._on_backend_called_signal,
            dispatch_uid=self.__class__
        )

    def _on_backend_called_signal(self, sender, **kwargs):
        # Import below prevents an AppRegistryNotReady error on Django init.
        import dsmr_backup.services.backup
        dsmr_backup.services.backup.check()
        dsmr_backup.services.backup.sync()  # pragma: no cover
