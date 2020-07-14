from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DsmrInfluxdbConfig(AppConfig):
    name = 'dsmr_influxdb'
    verbose_name = _('InfluxDB')
