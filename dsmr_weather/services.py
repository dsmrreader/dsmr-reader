from decimal import Decimal
import logging

from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.conf import settings
import requests

from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.reading import TemperatureReading
import dsmr_frontend.services


logger = logging.getLogger('commands')


def should_update():
    """ Checks whether we should update yet. """
    weather_settings = WeatherSettings.get_solo()

    if not weather_settings.track:
        return False

    if weather_settings.next_sync is not None and timezone.now() < weather_settings.next_sync:
        return False

    return True


def read_weather():
    """ Reads the current weather state, if enabled, and stores it. """
    # Only when explicitly enabled in settings.
    if not should_update():
        return

    try:
        get_temperature_from_api()
    except Exception as error:
        logger.exception(error)

        # On any error, just try again in 5 minutes.
        WeatherSettings.objects.all().update(next_sync=timezone.now() + timezone.timedelta(minutes=5))
        dsmr_frontend.services.display_dashboard_message(message=_(
            'Failed to read Buienradar API: {}'.format(error)
        ))


def get_temperature_from_api():
    # For backend logging in Supervisor.
    logger.debug(' - Reading temperature from Buienradar: %s', settings.DSMRREADER_BUIENRADAR_API_URL)
    response = requests.get(settings.DSMRREADER_BUIENRADAR_API_URL)

    if response.status_code != 200:
        logger.error(' [!] Failed reading temperature: HTTP %s', response.status_code)
        raise EnvironmentError('Unexpected status code received')

    # Find our selected station.
    station_id = WeatherSettings.get_solo().buienradar_station
    station_data = [x for x in response.json()['actual']['stationmeasurements'] if x['stationid'] == station_id]

    if not station_data:
        raise EnvironmentError('Selected station info not found')

    temperature = station_data[0]['groundtemperature']
    logger.debug(' - Read temperature: %s', temperature)

    # Push next sync back for an hour.
    hour_mark = timezone.now().replace(minute=0, second=0, microsecond=0)
    TemperatureReading.objects.create(read_at=hour_mark, degrees_celcius=Decimal(temperature))
    WeatherSettings.objects.all().update(next_sync=hour_mark + timezone.timedelta(hours=1))
