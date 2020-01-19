from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ConsumptionAppConfig(AppConfig):
    name = 'dsmr_consumption'
    verbose_name = _('Consumption')
