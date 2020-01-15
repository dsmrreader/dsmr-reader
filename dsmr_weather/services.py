from decimal import Decimal
import logging

from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
import requests

from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.reading import TemperatureReading
import dsmr_frontend.services


logger = logging.getLogger('commands')


def run(scheduled_process):
    """ Reads the current weather state and stores it. """
    try:
        temperature_reading = get_temperature_from_api()
    except Exception as error:
        logger.exception(error)

        scheduled_process.delay(timezone.timedelta(hours=1))
        return dsmr_frontend.services.display_dashboard_message(message=_(
            'Failed to read Buienradar API: {}'.format(error)
        ))

    scheduled_process.reschedule(temperature_reading.read_at + timezone.timedelta(hours=1))


def get_temperature_from_api():
    # For backend logging in Supervisor.
    logger.debug('Buienradar: Reading temperature: %s', settings.DSMRREADER_BUIENRADAR_API_URL)

    try:
        response = requests.get(settings.DSMRREADER_BUIENRADAR_API_URL)
    except Exception as error:
        logger.exception(error)
        raise AssertionError(_('Failed to connect to or read from Buienradar API'))

    if response.status_code != 200:
        logger.error('Buienradar: Failed reading temperature: HTTP %s', response.status_code)
        raise AssertionError(_('Unexpected status code received'))

    # Find our selected station.
    station_id = WeatherSettings.get_solo().buienradar_station
    station_data = [x for x in response.json()['actual']['stationmeasurements'] if x['stationid'] == station_id]

    if not station_data:
        raise AssertionError(_('Selected station info not found'))

    temperature = station_data[0]['groundtemperature']
    logger.debug('Buienradar: Read temperature: %s', temperature)

    hour_mark = timezone.now().replace(minute=0, second=0, microsecond=0)
    return TemperatureReading.objects.create(read_at=hour_mark, degrees_celcius=Decimal(temperature))
