from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DataloggerAppConfig(AppConfig):
    name = 'dsmr_datalogger'
    verbose_name = _('Datalogger')
