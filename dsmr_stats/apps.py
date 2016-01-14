from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DsmrStatsAppConfig(AppConfig):
    name = 'dsmr_stats'
    verbose_name = _('DSMR Statistics')
