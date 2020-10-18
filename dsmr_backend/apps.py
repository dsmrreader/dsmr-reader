import warnings

from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig
from django.db import connection
from django.conf import settings

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backend.signals import request_status


class BackendAppConfig(AppConfig):
    """ The backend app solely exists for triggering a backend signal. """
    name = 'dsmr_backend'
    verbose_name = _('Backend (dsmr_backend)')

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


@receiver(request_status)
def check_scheduled_processes(**kwargs):
    from dsmr_backend.models.schedule import ScheduledProcess

    issues = []
    offset = timezone.now() - timezone.timedelta(
        minutes=settings.DSMRREADER_STATUS_ALLOWED_SCHEDULED_PROCESS_LAGG_IN_MINUTES
    )
    lagging_processes = ScheduledProcess.objects.filter(
        active=True,
        planned__lt=offset
    )

    for current in lagging_processes:
        issues.append(
            MonitoringStatusIssue(
                __name__,
                _('Process behind schedule: {}').format(current.name),
                current.planned
            )
        )

    return issues


@receiver(request_status)
def postgresql_check_database_size(**kwargs):  # pragma: nocover
    import dsmr_backend.services.backend

    pretty_size, bytes_size = dsmr_backend.services.backend.postgresql_total_database_size()

    if bytes_size < settings.DSMRREADER_STATUS_WARN_OVER_EXCESSIVE_DATABASE_SIZE:
        return

    return MonitoringStatusIssue(
        __name__,
        _('Database growing large: {}, consider data cleanup (if not already enabled)').format(pretty_size),
        timezone.now()
    )
