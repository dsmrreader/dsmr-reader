from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(AppConfig):
    name = 'dsmr_datalogger'
    verbose_name = _('Datalogger')
