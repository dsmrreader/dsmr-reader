from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import django.db.models.signals


class StatsAppConfig(AppConfig):
    name = 'dsmr_stats'
    verbose_name = _('Trend & statistics')

    def ready(self):
        from dsmr_datalogger.models.reading import DsmrReading
        django.db.models.signals.post_save.connect(
            receiver=self._on_dsmrreading_created_signal,
            dispatch_uid=self.__class__,
            sender=DsmrReading
        )

    def _on_dsmrreading_created_signal(self, instance, created, raw, **kwargs):
        # Skip new or imported (fixture) instances.
        if not created or raw:
            return

        import dsmr_stats.services
        dsmr_stats.services.update_electricity_statistics(reading=instance)
