from datetime import datetime, timedelta, time

from django.db import transaction
from django.utils import timezone
from django.conf import settings

from dsmr_stats.models.settings import StatsSettings
from dsmr_stats.models.statistics import ElectricityStatistics, GasStatistics
from dsmr_consumption.models.consumption import ElectricityConsumption
import dsmr_consumption.services


def analyze():
    """ Analyzes daily consumption and statistics to determine whether new analysis is required. """
    stats_settings = StatsSettings.get_solo()

    # Respect user setting.
    if not stats_settings.track:
        return

    try:
        # Determine the starting date used to construct new statistics.
        electricity_statistic = ElectricityStatistics.objects.all().order_by('-day')[0]
    except IndexError:
        try:
            # This will happen either the first time or when all statistics were flushed manually.
            first_consumption = ElectricityConsumption.objects.all().order_by('read_at')[0]
        except IndexError:
            # Well, it seems we don't have any cojsumption logged (yet) at all.
            return

        # We should use the day before the first consumption.
        latest_statistics_day = first_consumption.read_at.date() - timedelta(hours=24)
    else:
        # As we'll be searching starting on this day, make sure to select the next one.
        latest_statistics_day = electricity_statistic.day + timedelta(hours=24)

    # Localize, as we do not want to use UTC as day boundary.
    search_start = timezone.datetime(
        year=latest_statistics_day.year,
        month=latest_statistics_day.month,
        day=latest_statistics_day.day,
        tzinfo=settings.LOCAL_TIME_ZONE
    ) + timedelta(hours=1)  # BUG BUG BUG: Required dispite UTC!?

    try:
        # First the first day of consumptions available. If any.
        consumption_found = ElectricityConsumption.objects.filter(
            read_at__gt=search_start
        ).order_by('read_at')[0]
    except IndexError:
        # No data logged yet.
        return

    consumption_date = consumption_found.read_at.date()

    # Skip today, try again tomorrow. As we need a full day to pass first.
    now = timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
    if consumption_date == now.date():
        return

    # One day at a time to prevent backend blocking. Flushed statistics will be regenerated quickly
    # anyway.
    create_daily_statistics(day=consumption_date)


@transaction.atomic
def create_daily_statistics(day):
    """ Calculates and persists both electricity and gas statistics for a day. """
    consumption = dsmr_consumption.services.day_consumption(day=day)

    ElectricityStatistics.objects.create(
        day=day,
        electricity1=consumption['electricity1'],
        electricity2=consumption['electricity2'],
        electricity1_returned=consumption['electricity1_returned'],
        electricity2_returned=consumption['electricity2_returned'],
        electricity1_cost=consumption['electricity1_cost'],
        electricity2_cost=consumption['electricity2_cost'],
    )

    GasStatistics.objects.create(
        day=day,
        gas=consumption['gas'],
        gas_cost=consumption['gas_cost'],
    )


@transaction.atomic
def flush():
    """ Flushes al statistics stored. New ones will generated, providing the source data exists. """
    ElectricityStatistics.objects.all().delete()
    GasStatistics.objects.all().delete()
