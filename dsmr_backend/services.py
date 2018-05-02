from distutils.version import StrictVersion
import traceback
import sys
import re

import requests
from django.conf import settings
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_backend.models import ScheduledCall


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


def process_scheduled_calls():
    """ Calls the backend and all services required. """
    calls = ScheduledCall.objects.callable()
    sys.stdout.write('{}: Calling {} backend service(s)\n'.format(
        timezone.localtime(timezone.now()), len(calls)
    ))

    for current in calls:
        sys.stdout.write(' > {} Executing: {}\n'.format(
            timezone.localtime(timezone.now()), current
        ))

        try:
            current.execute()
        except Exception as error:
            # Add and print traceback to help debugging any issues raised.
            exception_traceback = traceback.format_tb(error.__traceback__, limit=100)
            exception_traceback = "\n".join(exception_traceback)

            sys.stdout.write(' >>> Uncaught exception :: {}\n'.format(error))
            sys.stdout.write(' >>> {} :: {}\n'.format(current, exception_traceback))
            sys.stderr.write(exception_traceback)

            # Do not hammer.
            current.delay(timezone.timedelta(seconds=10))
