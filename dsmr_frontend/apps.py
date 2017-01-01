from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AppConfig(AppConfig):
    name = 'dsmr_frontend'
    verbose_name = _('Frontend')

    def ready(self):
        # For some weird reason Django proposes this model for DELETION when executing 'makemigrations'.
        # This seems to prevent it somehow...
        from .models.message import Notification  # noqa: W0611
