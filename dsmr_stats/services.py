from datetime import time
import math

from dateutil.relativedelta import relativedelta
from django.db import transaction, connection, models
from django.db.models.aggregates import Avg, Sum, Min, Max
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_consumption.services
import dsmr_backend.services


def analyze():  # noqa: C901
    """ Analyzes daily consumption and statistics to determine whether new analysis is required. """
    try:
        # Determine the starting date used to construct new statistics.
        day_statistic = DayStatistics.objects.all().order_by('-day')[0]
    except IndexError:
        try:
            # This will happen either the first time or when all statistics were flushed manually.
            first_consumption = ElectricityConsumption.objects.all().order_by('read_at')[0]
        except IndexError:
            # Well, it seems we don't have any consumption logged (yet) at all.
            return

        # We should use the day before the first consumption.
        read_at = timezone.localtime(first_consumption.read_at)
        latest_statistics_day = read_at.date()
    else:
        # As we'll be searching starting on this day, make sure to select the next one.
        latest_statistics_day = timezone.make_aware(timezone.datetime(
            year=day_statistic.day.year,
            month=day_statistic.day.month,
            day=day_statistic.day.day,
        )) + timezone.timedelta(days=1)

    # Localize, as we do not want to use UTC as day boundary.
    search_start = timezone.make_aware(timezone.datetime(
        year=latest_statistics_day.year,
        month=latest_statistics_day.month,
        day=latest_statistics_day.day,
    ))

    try:
        # Find the first day of consumptions available. If any.
        consumption_found = ElectricityConsumption.objects.filter(
            read_at__gt=search_start
        ).order_by('read_at')[0]
    except IndexError:
        # Happens when no data is available yet.
        return

    consumption_date = timezone.localtime(consumption_found.read_at).date()
    now = timezone.localtime(timezone.now())

    # Skip today, try again tomorrow. As we need a full day to pass first.
    if consumption_date == now.date():
        return

    # Do not create status until we've passed the next day by a margin. Required due to delayed gas update by meters.
    if dsmr_backend.services.get_capabilities(capability='gas') and now.time() < time(hour=1, minute=15):
        # Skip for a moment.
        return

    day_start = timezone.make_aware(timezone.datetime(
        year=consumption_date.year,
        month=consumption_date.month,
        day=consumption_date.day,
        hour=0,
    ))

    # Also, make sure we have processed all readings from that day.
    day_processed = not DsmrReading.objects.unprocessed().filter(
        timestamp__gte=day_start,
        timestamp__lte=day_start + timezone.timedelta(hours=24),
    ).exists()

    if not day_processed:
        return

    # For backend logging in Supervisor.
    print(' - Creating day & hour statistics for: {}.'.format(day_start))

    with transaction.atomic():
        # One day at a time to prevent backend blocking. Flushed statistics will be regenerated quickly anyway.
        create_daily_statistics(day=consumption_date)

        for current_hour in range(0, 24 + 1):  # Current day + midnight of next day.
            hour_start = day_start + timezone.timedelta(hours=current_hour)
            create_hourly_statistics(hour_start=hour_start)

    # Reflect changes in cache.
    cache.clear()


def create_daily_statistics(day):
    """ Calculates and persists both electricity and gas statistics for a day. Daily. """
    consumption = dsmr_consumption.services.day_consumption(day=day)

    return DayStatistics.objects.create(
        day=day,
        total_cost=consumption['total_cost'],

        electricity1=consumption['electricity1'],
        electricity2=consumption['electricity2'],
        electricity1_returned=consumption['electricity1_returned'],
        electricity2_returned=consumption['electricity2_returned'],
        electricity1_cost=consumption['electricity1_cost'],
        electricity2_cost=consumption['electricity2_cost'],

        gas=consumption.get('gas', 0),
        gas_cost=consumption.get('gas_cost', 0),

        lowest_temperature=consumption.get('lowest_temperature'),
        highest_temperature=consumption.get('highest_temperature'),
        average_temperature=consumption.get('average_temperature'),
    )


def create_hourly_statistics(hour_start):
    """ Calculates and persists both electricity and gas statistics for a day. Hourly. """
    hour_end = hour_start + timezone.timedelta(hours=1)
    electricity_readings, gas_readings = dsmr_consumption.services.consumption_by_range(
        start=hour_start, end=hour_end
    )

    if not electricity_readings.exists():
        return

    creation_kwargs = {
        'hour_start': hour_start
    }

    if HourStatistics.objects.filter(**creation_kwargs).exists():
        return

    electricity_start = electricity_readings[0]
    electricity_end = electricity_readings[electricity_readings.count() - 1]
    creation_kwargs['electricity1'] = electricity_end.delivered_1 - electricity_start.delivered_1
    creation_kwargs['electricity2'] = electricity_end.delivered_2 - electricity_start.delivered_2
    creation_kwargs['electricity1_returned'] = electricity_end.returned_1 - electricity_start.returned_1
    creation_kwargs['electricity2_returned'] = electricity_end.returned_2 - electricity_start.returned_2

    # DSMR v4.
    if len(gas_readings) == 1:
        creation_kwargs['gas'] = gas_readings[0].currently_delivered

    # DSMR v5
    elif len(gas_readings) > 1:
        gas_readings = list(gas_readings)
        creation_kwargs['gas'] = gas_readings[-1].delivered - gas_readings[0].delivered

    HourStatistics.objects.create(**creation_kwargs)


def clear_statistics():
    """ Clears ALL statistics ever generated. """
    DayStatistics.objects.all().delete()
    HourStatistics.objects.all().delete()


def electricity_tariff_percentage(start_date):
    """ Returns the total electricity consumption percentage by tariff (high/low tariff). """
    totals = DayStatistics.objects.filter(day__gte=start_date).aggregate(
        electricity1=Sum('electricity1'),
        electricity2=Sum('electricity2'),
    )

    # Empty data will crash.
    if not all(totals.values()):
        return None

    global_total = totals['electricity1'] + totals['electricity2']
    totals['electricity1'] = math.ceil(totals['electricity1'] / global_total * 100)
    totals['electricity2'] = 100 - totals['electricity1']
    return totals


def average_consumption_by_hour(max_weeks_ago):
    """ Calculates the average consumption by hour. Measured over all consumption data of the past X months. """
    sql_extra = {
        # Ugly engine check, but still beter than iterating over a hundred thousand items in code.
        'postgresql': "date_part('hour', hour_start)",
        'sqlite': "strftime('%H', hour_start)",
        'mysql': "extract(hour from hour_start)",
    }[connection.vendor]

    # Only PostgreSQL supports this builtin.
    set_time_zone_sql = connection.ops.set_time_zone_sql()

    if set_time_zone_sql:
        connection.connection.cursor().execute(set_time_zone_sql, [settings.TIME_ZONE])  # pragma: no cover

    hour_statistics = HourStatistics.objects.filter(
        # This greatly helps reducing the queryset size, but also makes it more relevant.
        hour_start__gt=timezone.now() - timezone.timedelta(weeks=max_weeks_ago)
    ).extra({
        'hour_start': sql_extra
    }).values('hour_start').order_by('hour_start').annotate(
        avg_electricity1=Avg('electricity1'),
        avg_electricity2=Avg('electricity2'),
        avg_electricity1_returned=Avg('electricity1_returned'),
        avg_electricity2_returned=Avg('electricity2_returned'),
        avg_electricity_merged=Avg(models.F('electricity1') + models.F('electricity2')),
        avg_electricity_returned_merged=Avg(models.F('electricity1_returned') + models.F('electricity2_returned')),
        avg_gas=Avg('gas'),
    )
    # Force evaluation, as we want to reset timezone in cursor below.
    hour_statistics = list(hour_statistics)

    if set_time_zone_sql:
        # Prevents "database connection isn't set to UTC" error.
        connection.connection.cursor().execute(set_time_zone_sql, ['UTC'])  # pragma: no cover

    return hour_statistics


def range_statistics(start, end):
    """ Returns the statistics (totals) for a target date. Its month will be used. """
    return DayStatistics.objects.filter(day__gte=start, day__lt=end).aggregate(
        total_cost=Sum('total_cost'),
        electricity1=Sum('electricity1'),
        electricity1_cost=Sum('electricity1_cost'),
        electricity1_returned=Sum('electricity1_returned'),
        electricity2=Sum('electricity2'),
        electricity2_cost=Sum('electricity2_cost'),
        electricity2_returned=Sum('electricity2_returned'),
        electricity_merged=Sum(models.F('electricity1') + models.F('electricity2')),
        electricity_cost_merged=Sum(models.F('electricity1_cost') + models.F('electricity2_cost')),
        electricity_returned_merged=Sum(models.F('electricity1_returned') + models.F('electricity2_returned')),
        gas=Sum('gas'),
        gas_cost=Sum('gas_cost'),
        temperature_min=Min('lowest_temperature'),
        temperature_max=Max('highest_temperature'),
        temperature_avg=Avg('average_temperature'),
    )


def day_statistics(target_date):
    """ Alias of daterange_statistics() for a day targeted. """
    next_day = timezone.datetime.combine(target_date + relativedelta(days=1), time.min)
    return range_statistics(start=target_date, end=next_day)


def month_statistics(target_date):
    """ Alias of daterange_statistics() for a month targeted. """
    start_of_month = timezone.datetime(year=target_date.year, month=target_date.month, day=1)
    end_of_month = timezone.datetime.combine(start_of_month + relativedelta(months=1), time.min)

    return range_statistics(start=start_of_month, end=end_of_month)


def year_statistics(target_date):
    """ Alias of daterange_statistics() for a year targeted. """
    start_of_year = timezone.datetime(year=target_date.year, month=1, day=1)
    end_of_year = timezone.datetime.combine(start_of_year + relativedelta(years=1), time.min)

    return range_statistics(start=start_of_year, end=end_of_year)
