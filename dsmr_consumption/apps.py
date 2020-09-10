from django.apps import AppConfig
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backend.signals import request_status
from dsmrreader import settings


class ConsumptionAppConfig(AppConfig):
    name = 'dsmr_consumption'
    verbose_name = _('Consumption')


@receiver(request_status)
def on_request_status(**kwargs):
    from dsmr_datalogger.models.reading import DsmrReading

    unprocessed_count = DsmrReading.objects.unprocessed().count()

    if unprocessed_count < settings.DSMRREADER_STATUS_MAX_UNPROCESSED_READINGS:
        return

    return [
        MonitoringStatusIssue(
            __name__,
            'Too many unprocessed readings: {}'.format(unprocessed_count),
            timezone.now()
        )
    ]
