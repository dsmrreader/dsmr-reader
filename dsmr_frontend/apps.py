from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FrontendAppConfig(AppConfig):
    name = 'dsmr_frontend'
    verbose_name = _('Frontend (dsmr_webinterface)')
