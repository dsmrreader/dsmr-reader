from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DsmrWeatherConfig(AppConfig):
    name = 'dsmr_weather'
    verbose_name = _('DSMR Weather')
