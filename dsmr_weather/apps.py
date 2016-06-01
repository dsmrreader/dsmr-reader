from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.db.models import signals as django_signals


class AppConfig(AppConfig):
    name = 'dsmr_weather'
    verbose_name = _('Weather')

    def ready(self):
        # Weather readings should be triggered by consumption updates. Dispatch UID prevents
        # duplicate signals.
        django_signals.post_save.connect(
            receiver=self._on_consumption_created_signal,
            dispatch_uid=self.__class__
        )

    def _on_consumption_created_signal(self, sender, instance, created, raw, **kwargs):
        # Import prevents an AppRegistryNotReady error on init.
        import dsmr_weather.services
        from dsmr_consumption.models.consumption import GasConsumption

        # We are only interested in new Gas readings.
        if not created or not isinstance(instance, GasConsumption):
            return

        # And they should not be imported by fixtures (raw) or migrations.
        if raw or sender.__name__ == 'Migration':
            return

        dsmr_weather.services.read_weather()
