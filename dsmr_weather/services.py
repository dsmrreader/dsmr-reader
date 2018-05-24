import xml.etree.ElementTree as ET
import urllib.request
from decimal import Decimal

from django.utils import timezone

from dsmr_weather.models.settings import WeatherSettings
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.buienradar import BUIENRADAR_API_URL, BUIENRADAR_XPATH


def should_sync():
    """ Checks whether we should sync yet. """
    weather_settings = WeatherSettings.get_solo()

    if not weather_settings.track:
        return False

    if weather_settings.next_sync is not None and timezone.now() < weather_settings.next_sync:
        return False

    return True


def read_weather():
    """ Reads the current weather state, if enabled, and stores it. """
    # Only when explicitly enabled in settings.
    if not should_sync():
        return

    # For backend logging in Supervisor.
    print(' - Performing temperature reading at Buienradar.')

    weather_settings = WeatherSettings.get_solo()

    try:
        # Fetch XML from API.
        request = urllib.request.urlopen(BUIENRADAR_API_URL)
    except Exception as e:
        print(' [!] Failed reading temperature: {}'.format(e))

        # Try again in 5 minutes.
        weather_settings.next_sync = timezone.now() + timezone.timedelta(minutes=5)
        weather_settings.save()
        return

    response_bytes = request.read()
    request.close()
    response_string = response_bytes.decode("utf8")

    # Use simplified xPath engine to extract current temperature.
    root = ET.fromstring(response_string)
    xpath = BUIENRADAR_XPATH.format(
        weather_station_id=weather_settings.buienradar_station
    )
    temperature_element = root.find(xpath)
    temperature = temperature_element.text
    print(' - Read temperature: {}'.format(temperature))

    # Gas readings trigger these readings, so the 'read at' timestamp should be somewhat in sync.
    # Therefor we align temperature readings with them, having them grouped by hour that is..
    read_at = timezone.now().replace(minute=0, second=0, microsecond=0)

    try:
        TemperatureReading.objects.create(read_at=read_at, degrees_celcius=Decimal(temperature))
    except Exception:
        # Try again in 5 minutes.
        weather_settings.next_sync = timezone.now() + timezone.timedelta(minutes=5)
    else:
        # Push next sync back for an hour.
        weather_settings.next_sync = read_at + timezone.timedelta(hours=1)

    weather_settings.save()
