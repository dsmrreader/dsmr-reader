import warnings

from django.utils.translation import ugettext_lazy as _
from django.apps import AppConfig
from django.db import connection
from django.conf import settings


class AppConfig(AppConfig):
    """ The backend app solely exists for triggering a backend signal. """
    name = 'dsmr_backend'
    verbose_name = _('Backend')

    def ready(self):
        """ Performs an DB engine check, as we maintain some engine specific queries. """
        if (connection.vendor not in settings.DSMRREADER_SUPPORTED_DB_VENDORS):  # pragma: no cover
            # Temporary for backwards compatibility
            warnings.showwarning(
                _(
                    'Unsupported database engine "{}" active, '
                    'some features might not work properly'.format(connection.vendor)
                ),
                RuntimeWarning, __file__, 0
            )
