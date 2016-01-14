from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from dsmrreader import signals


class DsmrWeatherAppConfig(AppConfig):
    name = 'dsmr_weather'
    verbose_name = _('DSMR Weather')

    def ready(self):
        # Weather readings should be triggered by consumption updates.
        signals.gas_consumption_created.connect(
            receiver=self._on_consumption_created_signal,
            dispatch_uid=self.__class__
        )

    def _on_consumption_created_signal(self, sender, **kwargs):
        # We do not care about the sender or instance. Import prevents AppRegistryNotReady error.
        import dsmr_weather.services
        dsmr_weather.services.read_weather()
