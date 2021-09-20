from datetime import time
import logging
import random
import json

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import requests

from dsmr_backend.dto import Capability
from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_consumption.models.consumption import GasConsumption
import dsmr_backend.services.backend
import dsmr_frontend.services


logger = logging.getLogger('dsmrreader')


def run(scheduled_process: ScheduledProcess):
    mindergas_settings = MinderGasSettings.get_solo()

    # Only when enabled and token set.
    if not mindergas_settings.auth_token:
        return mindergas_settings.update(export=False)  # Should also disable SP.

    # Nonsense when having no data.
    if not dsmr_backend.services.backend.get_capability(Capability.GAS):
        return scheduled_process.delay(hours=1)

    try:
        export()
    except Exception as error:
        logger.exception(error)

        scheduled_process.delay(hours=1)
        return dsmr_frontend.services.display_dashboard_message(message=_(
            'Failed to export to MinderGas: {}'.format(error)
        ))

    # Reschedule between 3 AM and 6 AM next day.
    midnight = timezone.localtime(timezone.make_aware(
        timezone.datetime.combine(timezone.now(), time.min)
    ))
    next_midnight = midnight + timezone.timedelta(
        hours=dsmr_backend.services.backend.hours_in_day(
            day=timezone.now().date()
        )
    )
    scheduled_process.reschedule(
        next_midnight + timezone.timedelta(
            hours=random.randint(3, 5),
            minutes=random.randint(15, 59)
        )
    )


def export():
    """ Exports gas readings to the MinderGas website. """
    mindergas_settings = MinderGasSettings.get_solo()
    midnight = timezone.localtime(timezone.make_aware(
        timezone.datetime.combine(timezone.now(), time.min)
    ))

    try:
        last_gas_reading = GasConsumption.objects.filter(
            # Slack of a few hours to make sure we have any valid reading at all.
            read_at__range=(midnight - timezone.timedelta(hours=3), midnight)
        ).order_by('-read_at')[0]
    except IndexError:
        raise AssertionError(_('No recent gas reading found'))

    reading_date = last_gas_reading.read_at.date().isoformat()
    logger.debug('MinderGas: Uploading gas meter position: %s m3 @ %s', last_gas_reading.delivered, reading_date)
    response = requests.post(
        MinderGasSettings.API_URL,
        headers={
            'User-Agent': settings.DSMRREADER_USER_AGENT,
            'Content-Type': 'application/json',
            'AUTH-TOKEN': mindergas_settings.auth_token
        },
        data=json.dumps({
            'date': reading_date,
            'reading': str(last_gas_reading.delivered)
        }),
    )

    if response.status_code != 201:
        logger.error('MinderGas: Upload failed (HTTP %s): %s', response.status_code, response.text)
        raise AssertionError(_('Unexpected status code received'))
