from io import StringIO
from typing import Optional, List, NoReturn
from unittest import mock

from django.core.management import call_command
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps import AppConfig
from django.db import connection
from django.conf import settings
from django.core.checks import Warning, Critical, register, Tags

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backend.signals import request_status


class BackendAppConfig(AppConfig):
    """ The backend app solely exists for triggering a backend signal. """
    name = 'dsmr_backend'
    verbose_name = _('Backend (dsmr_backend)')

    def ready(self) -> NoReturn:  # pragma: no cover
        @register(Tags.compatibility, deploy=True)
        def system_checks(app_configs, **kwargs) -> List:
            """ @see https://docs.djangoproject.com/en/3.1/topics/checks/"""
            errors = []

            # DB Engine check.
            if connection.vendor not in settings.DSMRREADER_SUPPORTED_DB_VENDORS:  # pragma: no cover
                errors.append(
                    Warning(
                        'Unsupported database engine "{}" active, some features might not work properly'.format(
                            connection.vendor
                        ),
                        obj=None,
                        id=settings.DSMRREADER_SYSTEM_CHECK_001,
                    )
                )

            # Check unapplied migrations.
            with mock.patch('sys.exit') as exit_mock:  # Prevent hard exit
                exit_mock.side_effect = InterruptedError()
                stdout = StringIO()

                try:
                    call_command('migrate', stdout=stdout, plan=True, check_unapplied=True, no_color=True)
                except InterruptedError:
                    stdout.seek(0)
                    migrate_output = stdout.read()

                    if migrate_output:  # e.g. " Alter field phase_voltage_l2 on dsmrreading"
                        errors.append(
                            Critical(
                                'There are unapplied migrations, please run "migrate"\n\n{}'.format(migrate_output),
                                obj=None,
                                id=settings.DSMRREADER_SYSTEM_CHECK_002,
                            )
                        )

            return errors


@receiver(request_status)
def check_scheduled_processes(**kwargs) -> List[MonitoringStatusIssue]:
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
def postgresql_check_database_size(**kwargs) -> Optional[MonitoringStatusIssue]:  # pragma: nocover
    import dsmr_backend.services.backend

    pretty_size, bytes_size = dsmr_backend.services.backend.postgresql_total_database_size()

    if bytes_size < settings.DSMRREADER_STATUS_WARN_OVER_EXCESSIVE_DATABASE_SIZE:
        return

    return MonitoringStatusIssue(
        __name__,
        _('Database growing large: {}, consider data cleanup (if not already enabled)').format(pretty_size),
        timezone.now()
    )
