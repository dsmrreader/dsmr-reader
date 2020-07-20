import logging

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


logger = logging.getLogger('dsmrreader')


class WeatherAppConfig(AppConfig):
    name = 'dsmr_weather'
    verbose_name = _('Weather')
