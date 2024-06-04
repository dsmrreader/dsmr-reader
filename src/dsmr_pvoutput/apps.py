from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PvoutputAppConfig(AppConfig):
    name = "dsmr_pvoutput"
    verbose_name = _("PVOutput")
