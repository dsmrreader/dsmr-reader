from datetime import timedelta

from django.db import transaction, connection
from django.utils import timezone
from django.conf import settings

from dsmr_stats.models.settings import StatsSettings
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_consumption.models.consumption import ElectricityConsumption
import dsmr_consumption.services
from django.db.models.aggregates import Avg


def analyze():
    """ Analyzes daily consumption and statistics to determine whether new analysis is required. """
    stats_settings = StatsSettings.get_solo()

    # Respect user setting.
    if not stats_settings.track:
        return

    try:
        # Determine the starting date used to construct new statistics.
        electricity_statistic = DayStatistics.objects.all().order_by('-day')[0]
    except IndexError:
        try:
            # This will happen either the first time or when all statistics were flushed manually.
            first_consumption = ElectricityConsumption.objects.all().order_by('read_at')[0]
        except IndexError:
            # Well, it seems we don't have any consumption logged (yet) at all.
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

    for current_hour in range(0, 24):
        # Since we are already sinde an atomic() transaction, no further savepoints are required.
        create_hourly_statistics(day=day, hour=current_hour)

    return DayStatistics.objects.create(
        day=day,
        total_cost=consumption['total_cost'],

        electricity1=consumption['electricity1'],
        electricity2=consumption['electricity2'],
        electricity1_returned=consumption['electricity1_returned'],
        electricity2_returned=consumption['electricity2_returned'],
        electricity1_cost=consumption['electricity1_cost'],
        electricity2_cost=consumption['electricity2_cost'],

        gas=consumption['gas'],
        gas_cost=consumption['gas_cost'],

        average_temperature=consumption['average_temperature'],
    )


def create_hourly_statistics(day, hour):
    """ Calculates and persists both electricity and gas statistics for an hour. """
    hour_start = timezone.datetime(
        year=day.year,
        month=day.month,
        day=day.day,
        hour=hour,
        tzinfo=settings.LOCAL_TIME_ZONE
    )
    hour_end = hour_start + timezone.timedelta(hours=1)
    electricity_readings, gas_readings = dsmr_consumption.services.consumption_by_range(
        start=hour_start, end=hour_end
    )

    if not electricity_readings.exists():
        return

    creation_kwargs = {
        'hour_start': hour_start
    }

    electricity_start = electricity_readings[0]
    electricity_end = electricity_readings[electricity_readings.count() - 1]
    creation_kwargs['electricity1'] = electricity_end.delivered_1 - electricity_start.delivered_1
    creation_kwargs['electricity2'] = electricity_end.delivered_2 - electricity_start.delivered_2
    creation_kwargs['electricity1_returned'] = electricity_end.returned_1 - electricity_start.returned_1
    creation_kwargs['electricity2_returned'] = electricity_end.returned_2 - electricity_start.returned_2

    if gas_readings.exists():
        # Gas readings are unique per hour anyway.
        creation_kwargs['gas'] = gas_readings[0].currently_delivered

    return HourStatistics.objects.create(**creation_kwargs)


@transaction.atomic
def flush():
    """ Flushes al statistics stored. New ones will generated, providing the source data exists. """
    DayStatistics.objects.all().delete()
    HourStatistics.objects.all().delete()


def average_consumption_by_hour():
    """ Calculates the average consumption by hour. Measured over all consumption data. """
    SQL_EXTRA = {
        # Ugly engine check, but still beter than iterating over a hundred thousand items in code.
        'postgresql': "date_part('hour', hour_start)",
        'mysql': "extract(hour from hour_start)",
    }

    try:
        sql_extra = SQL_EXTRA[connection.vendor]
    except KeyError:
        raise NotImplementedError(connection.vendor)

    return HourStatistics.objects.extra({
        'hour_start': sql_extra
    }).values('hour_start').order_by('hour_start').annotate(
        avg_electricity1=Avg('electricity1'),
        avg_electricity2=Avg('electricity2'),
        avg_electricity1_returned=Avg('electricity1_returned'),
        avg_electricity2_returned=Avg('electricity2_returned'),
        avg_gas=Avg('gas'),
    )
