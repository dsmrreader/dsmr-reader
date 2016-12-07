from distutils.version import StrictVersion
import re

import requests
from django.conf import settings

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings


def get_capabilities(capability=None):
    """
    Returns the capabilities of the data tracked, such as whether the meter supports gas readings or
    if there have been any readings regarding electricity being returned.

    Optionally returns a single capability when requested.
    """
    capabilities = {
        # We rely on consumption because DSMR readings might be flushed in the future.
        'electricity': ElectricityConsumption.objects.exists(),
        'electricity_returned': ElectricityConsumption.objects.filter(
            # We can not rely on meter positions, as the manufacturer sometimes initializes meters
            # with testing data. So we just have to wait for the first power returned.
            currently_returned__gt=0
        ).exists(),
        'gas': GasConsumption.objects.exists(),
        'weather': WeatherSettings.get_solo().track and TemperatureReading.objects.exists()
    }
    capabilities['any'] = any(capabilities.values())

    # Single selection.
    if capability is not None:
        return capabilities[capability]

    return capabilities


def is_latest_version():
    """ Checks whether the current version is the latest one available on Github. """
    response = requests.get(settings.DSMR_LATEST_VERSION_FILE)

    local_version = '{}.{}.{}'.format(* settings.DSMR_RAW_VERSION[:3])
    remote_version = re.search(r'^VERSION = \((\d+), (\d+), (\d+),', str(response.content, 'utf-8'), flags=re.MULTILINE)
    remote_version = '.'.join(remote_version.groups())

    return StrictVersion(local_version) >= StrictVersion(remote_version)
