from distutils.version import StrictVersion
import datetime

import requests
from django.db.migrations.recorder import MigrationRecorder
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache

from dsmr_backend import signals
from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_backend.models.settings import BackendSettings
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_influxdb.models import InfluxdbMeasurement, InfluxdbIntegrationSettings
from dsmr_mqtt.models.queue import Message
from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_stats.models.statistics import DayStatistics
from dsmr_backup.models.settings import BackupSettings, DropboxSettings
from dsmr_pvoutput.models.settings import PVOutputAddStatusSettings


def get_capabilities(capability=None):
    """
    Returns the capabilities of the data tracked, such as whether the meter supports gas readings or
    if there have been any readings regarding electricity being returned.

    Optionally returns a single capability when requested.
    """
    # Caching time should be limited, but enough to make it matter, as this call is used A LOT.
    capabilities = cache.get('capabilities')

    if capabilities is None:
        capabilities = {
            # We rely on consumption because source readings might be deleted after a while.
            'electricity': ElectricityConsumption.objects.exists(),
            'electricity_returned': ElectricityConsumption.objects.filter(
                # We can not rely on meter positions, as the manufacturer sometimes initializes meters
                # with testing data. So we just have to wait for the first power returned.
                currently_returned__gt=0
            ).exists(),
            'multi_phases': ElectricityConsumption.objects.filter(
                Q(
                    phase_currently_delivered_l2__isnull=False,
                ) | Q(
                    phase_currently_delivered_l3__isnull=False,
                ) | Q(
                    phase_voltage_l2__isnull=False,
                ) | Q(
                    phase_voltage_l3__isnull=False,
                )
            ).exists(),
            'voltage': ElectricityConsumption.objects.filter(
                phase_voltage_l1__isnull=False,
            ).exists(),
            'power_current': ElectricityConsumption.objects.filter(
                phase_power_current_l1__isnull=False,
            ).exists(),
            'gas': GasConsumption.objects.exists(),
            'weather': WeatherSettings.get_solo().track and TemperatureReading.objects.exists()
        }

        # Override capabilities when requested.
        backend_settings = BackendSettings.get_solo()

        if backend_settings.disable_gas_capability:
            capabilities['gas'] = False

        if backend_settings.disable_electricity_returned_capability:
            capabilities['electricity_returned'] = False

        capabilities['any'] = any(capabilities.values())
        cache.set('capabilities', capabilities)

    # Single selection.
    if capability is not None:
        return capabilities[capability]

    return capabilities


def is_latest_version():
    """ Checks whether the current version is the latest tagged available on Github. """
    response = requests.get(settings.DSMRREADER_LATEST_TAGS_LIST)
    latest_tag = response.json()[0]

    local_version = '{}.{}.{}'.format(* settings.DSMRREADER_RAW_VERSION[:3])
    remote_version = latest_tag['name'].replace('v', '')

    return StrictVersion(local_version) >= StrictVersion(remote_version)


def is_timestamp_passed(timestamp):
    """ Generic service to check whether a timestamp has passed/is happening or is empty (None). """
    if timestamp is None:
        return True

    return timezone.now() >= timestamp


def request_monitoring_status():
    """ Requests all apps to report any issues for monitoring. """
    responses = signals.request_status.send_robust(None)
    issues = []

    for current_receiver, current_response in responses:
        if not current_response or not isinstance(current_response, (list, tuple)):
            continue

        issues += current_response

    issues = sorted(issues, key=lambda x: x.since, reverse=True)

    return issues


def is_recent_installation():
    """ Checks whether this is a new installation, by checking the interval to the first migration. """
    has_old_migration = MigrationRecorder.Migration.objects.filter(
        applied__lt=timezone.now() - timezone.timedelta(hours=1)
    ).exists()
    return not has_old_migration


def hours_in_day(day):
    """ Returns the number of hours in a day. Should always be 24, except in DST transitions. """
    start = timezone.make_aware(timezone.datetime.combine(day, datetime.time.min))
    end = start + timezone.timedelta(days=1)
    start = timezone.localtime(start)
    end = timezone.localtime(end)

    # CEST -> CET
    if start.dst() > end.dst():
        return 25
    # CET -> CEST
    elif end.dst() > start.dst():
        return 23
    # Unchanged
    else:
        return 24
