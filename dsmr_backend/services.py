from distutils.version import StrictVersion
import re

import requests
from django.conf import settings
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_stats.models.statistics import DayStatistics


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
        'multi_phases': ElectricityConsumption.objects.filter(
            phase_currently_delivered_l2__isnull=False,
            phase_currently_delivered_l3__isnull=False
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
    response = requests.get(settings.DSMRREADER_LATEST_VERSION_FILE)

    local_version = '{}.{}.{}'.format(* settings.DSMRREADER_RAW_VERSION[:3])
    remote_version = re.search(r'^VERSION = \((\d+), (\d+), (\d+),', str(response.content, 'utf-8'), flags=re.MULTILINE)
    remote_version = '.'.join(remote_version.groups())

    return StrictVersion(local_version) >= StrictVersion(remote_version)


def is_timestamp_passed(timestamp):
    """ Generic service to check whether a timestamp has passed/is happening or is empty (None). """
    if timestamp is None:
        return True

    return timezone.now() >= timestamp


def status_info():
    """ Returns the status info of the application. """
    capabilities = get_capabilities()
    status = {
        'capabilities': capabilities,
        'electricity': {
            'latest': None,
            'minutes_since': None,
        },
        'gas': {
            'latest': None,
            'hours_since': None,
        },
        'readings': {
            'latest': None,
            'seconds_since': None,
            'unprocessed': {
                'count': None,
                'seconds_since': None,
            },
        },
        'statistics': {
            'latest': None,
            'days_since': None,
        },
    }

    status['readings']['unprocessed']['count'] = DsmrReading.objects.unprocessed().count()

    try:
        first_unprocessed_reading = DsmrReading.objects.unprocessed().order_by('timestamp')[0]
    except IndexError:
        pass
    else:
        diff = timezone.now() - first_unprocessed_reading.timestamp
        status['readings']['unprocessed']['seconds_since'] = round(diff.total_seconds())

    try:
        status['readings']['latest'] = DsmrReading.objects.all().order_by('-pk')[0].timestamp
    except IndexError:
        pass
    else:
        # It seems that smart meters sometimes have their clock set into the future, so we correct it.
        if status['readings']['latest'] > timezone.now():
            status['readings']['seconds_since'] = 0
            status['readings']['latest'] = timezone.now()
        else:
            diff = timezone.now() - status['readings']['latest']
            status['readings']['seconds_since'] = round(diff.total_seconds())

    if capabilities['electricity']:
        status['electricity']['latest'] = ElectricityConsumption.objects.all().order_by('-pk')[0].read_at
        diff = timezone.now() - status['electricity']['latest']
        status['electricity']['minutes_since'] = round(diff.total_seconds() / 60)

    if capabilities['gas']:
        status['gas']['latest'] = GasConsumption.objects.all().order_by('-pk')[0].read_at
        diff = timezone.now() - status['gas']['latest']
        status['gas']['hours_since'] = round(diff.total_seconds() / 3600)

    try:
        status['statistics']['latest'] = DayStatistics.objects.all().order_by('-day')[0].day
    except IndexError:
        pass
    else:
        status['statistics']['days_since'] = (
            timezone.now().date() - status['statistics']['latest']
        ).days

    return status
