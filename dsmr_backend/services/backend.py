import logging
from distutils.version import StrictVersion
import datetime
from typing import List, Optional, Tuple

import requests
from django.db.migrations.recorder import MigrationRecorder
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.db import connection

from dsmr_backend import signals
from dsmr_backend.dto import MonitoringStatusIssue, Capability, CapabilityReport
from dsmr_backend.models.settings import BackendSettings
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings


logger = logging.getLogger("dsmrreader")


def get_capabilities() -> CapabilityReport:  # noqa: C901
    """
    Returns the capabilities of the data tracked, such as whether the meter supports gas readings or
    if there have been any readings regarding electricity being returned.
    """
    # Caching time should be limited, but enough to make it matter, as this call is used A LOT.
    capability_report = cache.get(settings.DSMRREADER_CAPABILITIES_CACHE)

    if capability_report is not None:
        return capability_report

    # Override capabilities when requested.
    backend_settings = BackendSettings.get_solo()

    capability_report = CapabilityReport()

    # We rely on consumption because source readings might be deleted after a while.
    if ElectricityConsumption.objects.exists():
        capability_report.add(Capability.ELECTRICITY)

    # We can not rely on meter positions, as the manufacturer sometimes initializes meters
    # with testing data. So we just have to wait for the first power returned.
    if (
        not backend_settings.disable_electricity_returned_capability
        and ElectricityConsumption.objects.filter(currently_returned__gt=0).exists()
    ):
        capability_report.add(Capability.ELECTRICITY_RETURNED)

    if ElectricityConsumption.objects.filter(
        Q(
            phase_currently_delivered_l2__isnull=False,
        )
        | Q(
            phase_currently_delivered_l3__isnull=False,
        )
        | Q(
            phase_voltage_l2__isnull=False,
        )
        | Q(
            phase_voltage_l3__isnull=False,
        )
    ).exists():
        capability_report.add(Capability.MULTI_PHASES)

    if ElectricityConsumption.objects.filter(phase_voltage_l1__isnull=False).exists():
        capability_report.add(Capability.VOLTAGE)

    if ElectricityConsumption.objects.filter(
        phase_power_current_l1__isnull=False
    ).exists():
        capability_report.add(Capability.POWER_CURRENT)

    if not backend_settings.disable_gas_capability and GasConsumption.objects.exists():
        capability_report.add(Capability.GAS)

    if WeatherSettings.get_solo().track and TemperatureReading.objects.exists():
        capability_report.add(Capability.WEATHER)

    if EnergySupplierPrice.objects.exists():
        capability_report.add(Capability.COSTS)

    if len(capability_report) > 0:
        capability_report.add(Capability.ANY)

    cache.set(settings.DSMRREADER_CAPABILITIES_CACHE, capability_report)

    return capability_report


def get_capability(capability: Capability) -> bool:
    """Returns the status for a specific capability."""
    return capability in get_capabilities()


def is_latest_version() -> bool:
    """Checks whether the current version is the latest tagged available on GitHub."""
    response = requests.get(
        settings.DSMRREADER_LATEST_RELEASES_LIST,
        timeout=settings.DSMRREADER_CLIENT_TIMEOUT,
    )

    for current_release in response.json():
        # Ignore release candidates or drafts.
        if current_release["prerelease"] or current_release["draft"]:
            continue

        # Ignore other branches.
        if not current_release["tag_name"].startswith(settings.DSMRREADER_MAIN_BRANCH):
            continue

        release_tag = current_release["tag_name"].replace("v", "")
        local_version = "{}.{}.{}".format(*settings.DSMRREADER_RAW_VERSION[:3])

        # StrictVersion does not support dashes nor rc's
        # @see https://www.python.org/dev/peps/pep-0386/
        comparable_release_tag = release_tag.replace("-", "").replace("rc", "b")

        # Ignore same or lower releases.
        if StrictVersion(comparable_release_tag) <= StrictVersion(local_version):
            continue

        return False

    return True


def is_timestamp_passed(timestamp: Optional[timezone.datetime]) -> bool:
    """Generic service to check whether a timestamp has passed/is happening or is empty (None)."""
    if timestamp is None:
        return True

    return timezone.now() >= timestamp


def request_cached_monitoring_status():
    cached_monitoring_status = cache.get(settings.DSMRREADER_MONITORING_CACHE)

    if cached_monitoring_status is None:
        # This will also update the cache.
        return request_monitoring_status()

    return cached_monitoring_status  # pragma: nocover


def request_monitoring_status() -> List[MonitoringStatusIssue]:
    """Requests all apps to report any issues for monitoring."""
    responses = signals.request_status.send_robust(None)
    issues = []

    for _, current_response in responses:
        if not current_response:
            continue

        if isinstance(current_response, Exception):
            logger.warning(current_response)
            continue

        if not isinstance(current_response, (list, tuple)):
            current_response = [current_response]

        for x in current_response:
            if isinstance(x, MonitoringStatusIssue):
                issues.append(x)

    issues = sorted(issues, key=lambda y: y.since, reverse=True)

    # Always invalidate and update cache
    cache.set(settings.DSMRREADER_MONITORING_CACHE, issues)

    return issues


def is_recent_installation() -> bool:
    """Checks whether this is a new installation, by checking the interval to the first migration."""
    has_old_migration = MigrationRecorder.Migration.objects.filter(
        applied__lt=timezone.now() - timezone.timedelta(hours=1)
    ).exists()
    return not has_old_migration


def hours_in_day(day: datetime.date) -> int:
    """Returns the number of hours in a day. Should always be 24, except in DST transitions."""
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


def postgresql_total_database_size() -> Tuple[int, int]:  # pragma: nocover
    with connection.cursor() as cursor:
        database_name = settings.DATABASES["default"]["NAME"]
        size_sql = """
        SELECT pg_catalog.pg_size_pretty(pg_catalog.pg_database_size(d.datname)) as pretty_size,
               pg_catalog.pg_database_size(d.datname) as bytes_size
        FROM pg_catalog.pg_database d
        WHERE d.datname = %s;
        """
        cursor.execute(size_sql, [database_name])

        return cursor.fetchone()
