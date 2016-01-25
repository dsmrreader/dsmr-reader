from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(AppConfig):
    """ The backend app solely exists for triggering a backend signal. """
    name = 'dsmr_backend'
    verbose_name = _('Backend')
