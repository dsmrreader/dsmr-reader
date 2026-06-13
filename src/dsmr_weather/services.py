from decimal import Decimal
import logging

import datetime
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
import requests

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.reading import TemperatureReading


logger = logging.getLogger("dsmrreader")

_STATIONS_CACHE_KEY = "buienradar_stations"


def get_buienradar_stations() -> list[tuple[int, str]]:
    cached: list[tuple[int, str]] | None = cache.get(_STATIONS_CACHE_KEY)
    if cached is not None:
        return cached

    try:
        response = requests.get(
            settings.DSMRREADER_BUIENRADAR_API_URL,
            timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
        )
        response.raise_for_status()
        stations = sorted(
            [
                (int(s["StationId"]), "Weather station {}".format(s["StationName"]))
                for s in response.json()["Actual"]["WeatherStationMeasurements"]
            ],
            key=lambda x: x[1],
        )
    except Exception:
        logger.warning("Buienradar: Failed to fetch station list")
        return []

    cache.set(_STATIONS_CACHE_KEY, stations, settings.DSMRREADER_BUIENRADAR_STATIONS_CACHE_TIMEOUT)
    return stations


def run(scheduled_process: ScheduledProcess) -> None:
    """Reads the current weather state and stores it."""
    try:
        temperature_reading = get_temperature_from_api()
    except Exception as error:
        logger.error("Buienradar: {}".format(error))

        scheduled_process.delay(hours=1)
        return

    scheduled_process.reschedule(temperature_reading.read_at + datetime.timedelta(hours=1))


def get_temperature_from_api() -> TemperatureReading:
    # For backend logging in Supervisor.
    logger.debug("Buienradar: Reading temperature: %s", settings.DSMRREADER_BUIENRADAR_API_URL)

    try:
        response = requests.get(
            settings.DSMRREADER_BUIENRADAR_API_URL,
            timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
        )
    except Exception as error:
        raise RuntimeError("Failed to read API: {}".format(error)) from error

    if response.status_code != 200:
        raise RuntimeError("Unexpected status code received: HTTP {}".format(response.status_code))

    # Find our selected station.
    station_id = WeatherSettings.get_solo().buienradar_station
    station_data = [x for x in response.json()["Actual"]["WeatherStationMeasurements"] if x["StationId"] == station_id]

    if not station_data:
        raise RuntimeError("Selected station info not found: {}".format(station_id))

    temperature = station_data[0]["Temperature"]
    logger.debug("Buienradar: Storing temperature read: %s", temperature)

    hour_mark = timezone.now().replace(minute=0, second=0, microsecond=0)
    return TemperatureReading.objects.create(read_at=hour_mark, degrees_celcius=Decimal(temperature))
