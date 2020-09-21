from django.apps import AppConfig
from django.conf import settings
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from dsmr_backend.dto import MonitoringStatusIssue
from dsmr_backend.signals import request_status


class ConsumptionAppConfig(AppConfig):
    name = 'dsmr_consumption'
    verbose_name = _('Consumption')


@receiver(request_status)
def check_unprocessed_readings(**kwargs):
    from dsmr_datalogger.models.reading import DsmrReading

    unprocessed_count = DsmrReading.objects.unprocessed().count()

    if unprocessed_count < settings.DSMRREADER_STATUS_MAX_UNPROCESSED_READINGS:
        return

    return [
        MonitoringStatusIssue(
            __name__,
            'Too many unprocessed readings: {}'.format(unprocessed_count),
            DsmrReading.objects.unprocessed().order_by('timestamp')[0].timestamp
        )
    ]
