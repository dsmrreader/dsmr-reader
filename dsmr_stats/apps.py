from typing import Optional

from django.apps import AppConfig
from django.conf import settings
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import django.db.models.signals

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backend.signals import request_status


class StatsAppConfig(AppConfig):
    name = 'dsmr_stats'
    verbose_name = _('Trend & statistics')

    def ready(self):
        from dsmr_datalogger.models.reading import DsmrReading
        django.db.models.signals.post_save.connect(
            receiver=self._on_dsmrreading_created_signal,
            dispatch_uid=self.__class__,
            sender=DsmrReading
        )

    def _on_dsmrreading_created_signal(self, instance, created, raw, **kwargs):
        # Skip new or imported (fixture) instances.
        if not created or raw:
            return

        import dsmr_stats.services
        dsmr_stats.services.update_electricity_statistics(reading=instance)


@receiver(request_status)
def check_day_statistics_generation(**kwargs) -> Optional[MonitoringStatusIssue]:
    from dsmr_stats.models.statistics import DayStatistics

    try:
        latest_day_statistics = DayStatistics.objects.all().order_by('-day')[0]
    except IndexError:
        return MonitoringStatusIssue(
            __name__,
            _('No day statistics found'),
            timezone.now()
        )

    offset = timezone.now().date() - timezone.timedelta(
        days=settings.DSMRREADER_STATUS_ALLOWED_DAY_STATISTICS_LAGG_IN_DAYS
    )

    latest_date_generated = latest_day_statistics.day

    if latest_date_generated > offset:
        return None

    return MonitoringStatusIssue(
        __name__,
        _('Day statistics are lagging behind'),
        timezone.make_aware(timezone.datetime(
            year=latest_date_generated.year,
            month=latest_date_generated.month,
            day=latest_date_generated.day,
            hour=23,
            minute=59
        ))
    )
