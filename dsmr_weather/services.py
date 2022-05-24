from decimal import Decimal
import logging
from typing import NoReturn

from django.utils import timezone
from django.conf import settings
import requests

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.reading import TemperatureReading


logger = logging.getLogger('dsmrreader')


def run(scheduled_process: ScheduledProcess) -> NoReturn:
    """ Reads the current weather state and stores it. """
    try:
        temperature_reading = get_temperature_from_api()
    except Exception as error:
        logger.error('Buienradar: {}'.format(error))

        scheduled_process.delay(hours=1)
        return

    scheduled_process.reschedule(temperature_reading.read_at + timezone.timedelta(hours=1))


def get_temperature_from_api() -> TemperatureReading:
    # For backend logging in Supervisor.
    logger.debug('Buienradar: Reading temperature: %s', settings.DSMRREADER_BUIENRADAR_API_URL)

    try:
        response = requests.get(
            settings.DSMRREADER_BUIENRADAR_API_URL,
            timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
        )
    except Exception as error:
        raise RuntimeError('Failed to read API: {}'.format(error)) from error

    if response.status_code != 200:
        raise RuntimeError('Unexpected status code received: HTTP {}'.format(response.status_code))

    # Find our selected station.
    station_id = WeatherSettings.get_solo().buienradar_station
    station_data = [x for x in response.json()['actual']['stationmeasurements'] if x['stationid'] == station_id]

    if not station_data:
        raise RuntimeError('Selected station info not found: {}'.format(station_id))

    temperature = station_data[0]['groundtemperature']
    logger.debug('Buienradar: Storing temperature read: %s', temperature)

    hour_mark = timezone.now().replace(minute=0, second=0, microsecond=0)
    return TemperatureReading.objects.create(read_at=hour_mark, degrees_celcius=Decimal(temperature))
