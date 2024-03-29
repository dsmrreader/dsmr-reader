from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

import dsmr_backend.signals


class NotificationAppConfig(AppConfig):
    name = "dsmr_notification"
    verbose_name = _("Notification apps")

    def ready(self):
        dsmr_backend.signals.backend_called.connect(
            receiver=self._on_backend_called_signal, dispatch_uid=self.__class__
        )

    def _on_backend_called_signal(self, sender, **kwargs):
        # Import below prevents an AppRegistryNotReady error on Django init.
        import dsmr_notification.services

        dsmr_notification.services.notify()
        dsmr_notification.services.check_status()
