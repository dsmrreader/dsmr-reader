from datetime import time
import logging
import random
import json

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
import requests

from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_consumption.models.consumption import GasConsumption
import dsmr_backend.services.backend
import dsmr_frontend.services


logger = logging.getLogger('commands')


def run(scheduled_process):
    mindergas_settings = MinderGasSettings.get_solo()

    # Only when enabled and token set.
    if not mindergas_settings.auth_token:
        return mindergas_settings.update(export=False)  # Should also disable SP.

    # Nonsense when having no data.
    if not dsmr_backend.services.backend.get_capabilities(capability='gas'):
        return scheduled_process.delay(timezone.timedelta(hours=1))

    try:
        export()
    except Exception as error:
        logger.exception(error)

        scheduled_process.delay(timezone.timedelta(hours=1))
        return dsmr_frontend.services.display_dashboard_message(message=_(
            'Failed to export to MinderGas: {}'.format(error)
        ))

    # Push back for a day and a bit.
    midnight = timezone.localtime(timezone.make_aware(
        timezone.datetime.combine(timezone.now(), time.min)
    ))
    scheduled_process.reschedule(midnight + timezone.timedelta(hours=24, minutes=random.randint(15, 59)))


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

    logger.debug('MinderGas: Uploading gas meter position: %s', last_gas_reading.delivered)
    response = requests.post(
        MinderGasSettings.API_URL,
        headers={
            'User-Agent': settings.DSMRREADER_USER_AGENT,
            'Content-Type': 'application/json',
            'AUTH-TOKEN': mindergas_settings.auth_token
        },
        data=json.dumps({
            'date': last_gas_reading.read_at.date().isoformat(),
            'reading': str(last_gas_reading.delivered)
        }),
    )

    if response.status_code != 201:
        logger.error('MinderGas: Upload failed (HTTP %s): %s', response.status_code, response.text)
        raise AssertionError(_('Invalid status code'))
