from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DsmrClientConfig(AppConfig):
    name = 'dsmr_client'
    verbose_name = _('Continuous client (dsmr_client)')
