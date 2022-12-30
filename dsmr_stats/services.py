import datetime
import logging

from decimal import Decimal
from datetime import time, date
import math
from typing import Dict, Optional, List

from dateutil.relativedelta import relativedelta
from django.db import transaction, connection, models
from django.db.models.aggregates import Avg, Sum, Min, Max, Count
from django.core.cache import cache
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.conf import settings

from dsmr_backend.dto import Capability
from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import (
    DayStatistics,
    HourStatistics,
    ElectricityStatistics,
)
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_backend.services.backend
import dsmr_consumption.services


logger = logging.getLogger("dsmrreader")


def is_data_available() -> bool:
    """Checks whether data is available for stats."""
    return ElectricityConsumption.objects.all().exists()


def get_next_day_to_generate() -> datetime.date:
    """Returns the next day to generate statistics for."""
    try:
        # By default just take the previous day we have statistics for.
        latest_day = DayStatistics.objects.all().order_by("-day")[0].day
    except IndexError:
        # Beginning of time.
        read_at = ElectricityConsumption.objects.all().order_by("read_at")[0].read_at
        return timezone.localtime(read_at).date()

    # Search for the next day with any consumption.
    next_day = latest_day + timezone.timedelta(days=1)
    search_start = timezone.datetime.combine(next_day, timezone.datetime.min.time())
    search_start = timezone.make_aware(search_start)

    try:
        next_consumption = ElectricityConsumption.objects.filter(
            read_at__gt=search_start
        ).order_by("read_at")[0]
    except IndexError:
        # Last resort.
        return next_day

    return timezone.localtime(next_consumption.read_at).date()


def run(scheduled_process: ScheduledProcess) -> None:
    """Analyzes daily consumption and statistics to determine whether new analysis is required."""
    if not is_data_available():
        logger.debug("Stats: No data available")
        scheduled_process.delay(hours=1)
        return

    now = timezone.localtime(timezone.now())
    target_day = get_next_day_to_generate()
    next_day = target_day + timezone.timedelta(days=1)

    # Skip current day, wait until midnight.
    if target_day >= now.date():
        logger.debug("Stats: Waiting for day to pass: %s", target_day)
        scheduled_process.reschedule(
            timezone.make_aware(timezone.datetime.combine(next_day, time.min))
        )
        return

    # All readings of the day must be processed.
    unprocessed_readings = (
        DsmrReading.objects.unprocessed().filter(timestamp__date=target_day).exists()
    )

    if unprocessed_readings:
        logger.debug("Stats: Found unprocessed readings for: %s", target_day)
        scheduled_process.delay(minutes=5)
        return

    # Ensure we have any consumption.
    consumption_found = ElectricityConsumption.objects.filter(
        read_at__date=target_day
    ).exists()

    if not consumption_found:
        logger.debug("Stats: Missing consumption data for: %s", target_day)
        scheduled_process.delay(hours=1)
        return

    # If we recently supported gas, make sure we've received a gas reading on the next day (or later).
    recently_gas_read = GasConsumption.objects.filter(
        read_at__date__gte=target_day - timezone.timedelta(days=1)
    ).exists()

    # Unless it was disabled.
    gas_capability = dsmr_backend.services.backend.get_capability(Capability.GAS)

    if (
        gas_capability
        and recently_gas_read
        and not GasConsumption.objects.filter(read_at__date__gte=next_day).exists()
    ):
        logger.debug("Stats: Waiting for first gas reading on the next day...")
        scheduled_process.delay(minutes=5)
        return

    create_statistics(target_day=target_day)

    # We keep trying until we've caught on to the current day (which will then delay it for a day above).
    scheduled_process.delay(seconds=1)
    return


def create_statistics(target_day: datetime.date) -> None:
    # One day at a time to prevent backend blocking.
    start_of_day = timezone.make_aware(
        timezone.datetime(
            year=target_day.year,
            month=target_day.month,
            day=target_day.day,
            hour=0,
        )
    )

    # Day and hour records should either be complete or not persisted at all.
    with transaction.atomic():
        hours_in_day = dsmr_backend.services.backend.hours_in_day(day=target_day)

        for current_hour in range(0, hours_in_day):
            hour_start = start_of_day + timezone.timedelta(hours=current_hour)
            create_hourly_statistics(hour_start=hour_start)

        instance = create_daily_statistics(day=target_day)
        instance.save()

    # Reflect changes in cache.
    cache.clear()


def create_daily_statistics(day: datetime.date) -> DayStatistics:
    """Calculates and returns a day summary. Does NOT persist!"""
    logger.debug("Stats: Creating day statistics for: %s", day)
    consumption = dsmr_consumption.services.day_consumption(day=day)

    hours_in_day = dsmr_backend.services.backend.hours_in_day(day=day)
    start_of_day = timezone.make_aware(
        timezone.datetime(year=day.year, month=day.month, day=day.day, hour=0, minute=0)
    )
    end_of_day = start_of_day + timezone.timedelta(hours=hours_in_day)

    logger.debug(
        "Stats: Searching for readings between %s and %s", start_of_day, end_of_day
    )

    # Fix for wrong gas consumption in some cases. Just use the hour totals instead.
    hours_gas_sum = HourStatistics.objects.filter(
        hour_start__gte=start_of_day,
        hour_start__lt=end_of_day,
    ).aggregate(gas_sum=Sum("gas"),)["gas_sum"]

    # First reading of the day for meter positions.
    first_electricity_reading_of_day = (
        DsmrReading.objects.filter(
            timestamp__gte=start_of_day,
            timestamp__lt=end_of_day,
        )
        .order_by("timestamp")
        .first()
    )

    if dsmr_backend.services.backend.get_capability(Capability.GAS):
        # Gas readings may lag a bit behind for DSMR v4 telegrams. Make sure the gas meter updated the timestamp!
        first_gas_reading_of_day = (
            DsmrReading.objects.filter(
                # DB indexed
                timestamp__gte=start_of_day,
                timestamp__lt=end_of_day,
                # No DB index
                extra_device_timestamp__gte=start_of_day,
                extra_device_timestamp__lt=end_of_day,
            )
            .order_by("extra_device_timestamp")
            .first()
        )
    else:
        first_gas_reading_of_day = None

    return DayStatistics(
        day=day,
        total_cost=consumption["total_cost"],
        electricity1=consumption["electricity1"],
        electricity2=consumption["electricity2"],
        electricity1_returned=consumption["electricity1_returned"],
        electricity2_returned=consumption["electricity2_returned"],
        electricity1_cost=consumption["electricity1_cost"],
        electricity2_cost=consumption["electricity2_cost"],
        # Gas is optional
        gas=hours_gas_sum or 0,
        # @TODO: May not be in sync with 'hours_gas_sum'!
        gas_cost=consumption.get("gas_cost", 0),
        lowest_temperature=consumption.get("lowest_temperature"),
        highest_temperature=consumption.get("highest_temperature"),
        average_temperature=consumption.get("average_temperature"),
        fixed_cost=consumption["fixed_cost"],
        # Historic reading summary. Use first readings of the day as reference.
        electricity1_reading=first_electricity_reading_of_day.electricity_delivered_1
        if first_electricity_reading_of_day
        else None,
        electricity2_reading=first_electricity_reading_of_day.electricity_delivered_2
        if first_electricity_reading_of_day
        else None,
        electricity1_returned_reading=first_electricity_reading_of_day.electricity_returned_1
        if first_electricity_reading_of_day
        else None,
        electricity2_returned_reading=first_electricity_reading_of_day.electricity_returned_2
        if first_electricity_reading_of_day
        else None,
        gas_reading=first_gas_reading_of_day.extra_device_delivered
        if first_gas_reading_of_day
        else None,
    )


def create_hourly_statistics(hour_start: timezone.datetime) -> Optional[HourStatistics]:
    """Calculates and returns an hour summary, when applicable. Persists it as well."""
    logger.debug("Stats: Creating hour statistics for: %s", hour_start)
    hour_end = hour_start + timezone.timedelta(hours=1)
    electricity_readings, gas_readings = dsmr_consumption.services.consumption_by_range(
        start=hour_start, end=hour_end
    )

    if not electricity_readings.exists():
        return

    creation_kwargs = {"hour_start": hour_start}

    if HourStatistics.objects.filter(**creation_kwargs).exists():
        logger.debug("Stats: Skipping duplicate hour statistics for: %s", hour_start)
        return

    electricity_start = electricity_readings.first()
    electricity_end = electricity_readings.last()
    creation_kwargs["electricity1"] = (
        electricity_end.delivered_1 - electricity_start.delivered_1
    )
    creation_kwargs["electricity2"] = (
        electricity_end.delivered_2 - electricity_start.delivered_2
    )
    creation_kwargs["electricity1_returned"] = (
        electricity_end.returned_1 - electricity_start.returned_1
    )
    creation_kwargs["electricity2_returned"] = (
        electricity_end.returned_2 - electricity_start.returned_2
    )

    # DSMR v4.
    if len(gas_readings) == 1:
        creation_kwargs["gas"] = gas_readings[0].currently_delivered

    # DSMR v5
    elif len(gas_readings) > 1:
        gas_readings = list(gas_readings)
        creation_kwargs["gas"] = gas_readings[-1].delivered - gas_readings[0].delivered

    return HourStatistics.objects.create(**creation_kwargs)


def clear_statistics() -> None:
    """Clears ALL statistics ever generated."""
    DayStatistics.objects.all().delete()
    HourStatistics.objects.all().delete()


def electricity_tariff_percentage(start: date, end: date) -> Optional[Dict]:
    """Returns the total electricity consumption percentage by tariff (high/low tariff)."""
    totals = DayStatistics.objects.filter(day__gte=start, day__lte=end,).aggregate(
        electricity1=Sum("electricity1"),
        electricity2=Sum("electricity2"),
    )

    # Summing up non-existent data results in None.
    totals = {k: v if v is not None else 0 for k, v in totals.items()}
    global_total = totals["electricity1"] + totals["electricity2"]

    try:
        totals["electricity1"] = math.ceil(totals["electricity1"] / global_total * 100)
        totals["electricity2"] = 100 - totals["electricity1"]
    except ZeroDivisionError:
        pass

    return totals


def average_consumption_by_hour(start: date, end: date) -> List:
    """Calculates the average consumption by hour. Measured over all consumption data of the past X months."""
    sql_extra = {
        # Ugly engine check, but still beter than iterating over a hundred thousand items in code.
        "postgresql": "date_part('hour', hour_start)",
        "sqlite": "strftime('%H', hour_start)",
        "mysql": "extract(hour from hour_start)",
    }[connection.vendor]

    # Only PostgreSQL supports this builtin.
    set_time_zone_sql = connection.ops.set_time_zone_sql()

    if set_time_zone_sql:
        connection.connection.cursor().execute(
            set_time_zone_sql, [settings.TIME_ZONE]
        )  # pragma: no cover

    hour_statistics = (
        HourStatistics.objects.filter(  # noqa: S610
            hour_start__date__gte=start,
            hour_start__date__lte=end,
        )
        .extra({"hour_start": sql_extra})
        .values("hour_start")
        .order_by("hour_start")
        .annotate(
            avg_electricity1=Avg("electricity1"),
            avg_electricity2=Avg("electricity2"),
            avg_electricity1_returned=Avg("electricity1_returned"),
            avg_electricity2_returned=Avg("electricity2_returned"),
            avg_electricity_merged=Avg(
                models.F("electricity1") + models.F("electricity2")
            ),
            avg_electricity_returned_merged=Avg(
                models.F("electricity1_returned") + models.F("electricity2_returned")
            ),
            avg_gas=Avg("gas"),
        )
    )
    # Force evaluation, as we want to reset timezone in cursor below.
    hour_statistics = list(hour_statistics)

    if set_time_zone_sql:
        # Prevents "database connection isn't set to UTC" error.
        connection.connection.cursor().execute(
            set_time_zone_sql, ["UTC"]
        )  # pragma: no cover

    return hour_statistics


def range_statistics(start: datetime.date, end: datetime.date):
    """Returns the statistics (totals) and the number of data points for a target range."""
    queryset = DayStatistics.objects.filter(day__gte=start, day__lt=end)
    aggregate = queryset.aggregate(
        electricity1=Sum("electricity1"),
        electricity1_cost=Sum("electricity1_cost"),
        electricity1_returned=Sum("electricity1_returned"),
        electricity2=Sum("electricity2"),
        electricity2_cost=Sum("electricity2_cost"),
        electricity2_returned=Sum("electricity2_returned"),
        electricity_merged=Sum(models.F("electricity1") + models.F("electricity2")),
        electricity_cost_merged=Sum(
            models.F("electricity1_cost") + models.F("electricity2_cost")
        ),
        electricity_returned_merged=Sum(
            models.F("electricity1_returned") + models.F("electricity2_returned")
        ),
        gas=Sum("gas"),
        gas_cost=Sum("gas_cost"),
        fixed_cost=Sum("fixed_cost"),
        total_cost=Sum("total_cost"),
        temperature_min=Min("lowest_temperature"),
        temperature_max=Max("highest_temperature"),
        temperature_avg=Avg("average_temperature"),
        number_of_days=Count("day"),
    )

    rounding = {
        # Decimals: [fields]
        2: (
            "electricity1_cost",
            "electricity2_cost",
            "electricity_cost_merged",
            "gas_cost",
            "fixed_cost",
            "total_cost",
        ),
        3: (
            "electricity1",
            "electricity1_returned",
            "electricity2",
            "electricity2_returned",
            "electricity_merged",
            "electricity_returned_merged",
            "gas",
        ),
    }

    # For some reason the values are not rounded and formatted like "0.0300000000000000". So we force rounding them.
    for decimal_count, fields in rounding.items():
        for current_field in fields:
            if aggregate[current_field] is None:
                continue

            aggregate[current_field] = dsmr_consumption.services.round_decimal(
                aggregate[current_field], decimal_count
            )

    return aggregate


def day_statistics(target_date: datetime.date):
    """Alias of range_statistics() for a day targeted."""
    next_day = timezone.datetime.combine(target_date + relativedelta(days=1), time.min)
    return range_statistics(start=target_date, end=next_day)


def month_statistics(target_date: datetime.date):
    """Alias of range_statistics() for a month targeted."""
    start_of_month = timezone.datetime(
        year=target_date.year, month=target_date.month, day=1
    )
    end_of_month = timezone.datetime.combine(
        start_of_month + relativedelta(months=1), time.min
    )
    return range_statistics(start=start_of_month, end=end_of_month)


def year_statistics(target_date: datetime.date):
    """Alias of range_statistics() for a year targeted."""
    start_of_year = timezone.datetime(year=target_date.year, month=1, day=1)
    end_of_year = timezone.datetime.combine(
        start_of_year + relativedelta(years=1), time.min
    )
    return range_statistics(start=start_of_year, end=end_of_year)


def period_totals() -> Dict:
    """Retrieves year/month period totals and merges them with today's consumption."""
    today = timezone.localtime(timezone.now())

    try:
        today_stats = dsmr_consumption.services.day_consumption(day=today)
    except LookupError:
        today_stats = {}

    month_stats = month_statistics(target_date=today)
    year_stats = year_statistics(target_date=today)
    excluded_keys = (
        "number_of_days",
        "temperature_avg",
        "temperature_min",
        "temperature_max",
    )

    for k in month_stats.keys():
        if k in excluded_keys or month_stats[k] is None:
            continue

        # Assumes same keys, zero value fallback.
        month_stats[k] += today_stats.get(k, 0)

    for k in year_stats.keys():
        if k in excluded_keys or year_stats[k] is None:
            continue

        # Assumes same keys, zero value fallback.
        year_stats[k] += today_stats.get(k, 0)

    return dict(
        day=today,
        today=today_stats,
        month=month_stats,
        year=year_stats,
    )


def update_electricity_statistics(reading: DsmrReading) -> None:
    """Updates the ElectricityStatistics records."""
    MAPPING = {
        # Stats record field: Reading field.
        "highest_usage_l1": "phase_currently_delivered_l1",
        "highest_usage_l2": "phase_currently_delivered_l2",
        "highest_usage_l3": "phase_currently_delivered_l3",
        "highest_return_l1": "phase_currently_returned_l1",
        "highest_return_l2": "phase_currently_returned_l2",
        "highest_return_l3": "phase_currently_returned_l3",
        "lowest_usage_l1": "phase_currently_delivered_l1",
        "lowest_usage_l2": "phase_currently_delivered_l2",
        "lowest_usage_l3": "phase_currently_delivered_l3",
    }
    stats = ElectricityStatistics.get_solo()
    dirty = False

    for stat_field, reading_field in MAPPING.items():
        reading_value = getattr(reading, reading_field) or 0
        top_value = getattr(stats, "{}_value".format(stat_field)) or 0

        if top_value == 0 and stat_field.startswith("lowest"):
            top_value = 9999999

        reading_value = Decimal(str(reading_value))
        top_value = Decimal(str(top_value))

        if not reading_value:
            continue

        # Depending on what we track, compare to the current high (or low).
        if (stat_field.startswith("lowest") and reading_value < top_value) or (
            stat_field.startswith("highest") and reading_value > top_value
        ):
            dirty = True
            setattr(stats, "{}_value".format(stat_field), reading_value)
            setattr(stats, "{}_timestamp".format(stat_field), reading.timestamp)

    if dirty:
        stats.save()


def recalculate_prices() -> None:
    """Retroactively sets the prices for all statistics. E.g.: When the user has altered the prices."""
    for current_day in DayStatistics.objects.all():
        print(" - Recalculating:", current_day.day)

        try:
            prices = dsmr_consumption.services.get_day_prices(day=current_day.day)
        except EnergySupplierPrice.DoesNotExist:
            print(" !!! No prices found, using zero fallback")
            prices = dsmr_consumption.services.get_fallback_prices()

        current_day.fixed_cost = prices.fixed_daily_cost
        current_day.electricity1_cost = dsmr_consumption.services.round_decimal(
            (current_day.electricity1 * prices.electricity_delivered_1_price)
            - (current_day.electricity1_returned * prices.electricity_returned_1_price)
        )
        current_day.electricity2_cost = dsmr_consumption.services.round_decimal(
            (current_day.electricity2 * prices.electricity_delivered_2_price)
            - (current_day.electricity2_returned * prices.electricity_returned_2_price)
        )

        total_cost = (
            current_day.electricity1_cost
            + current_day.electricity2_cost
            + current_day.fixed_cost
        )

        if current_day.gas is not None:
            current_day.gas_cost = dsmr_consumption.services.round_decimal(
                current_day.gas * prices.gas_price
            )
            total_cost += current_day.gas_cost

        current_day.total_cost = dsmr_consumption.services.round_decimal(total_cost)
        current_day.save()


def reconstruct_missing_day_statistics() -> None:
    """Reconstructs missing day statistics."""
    dates_to_generate = (
        ElectricityConsumption.objects.exclude(
            # Skip today.
            read_at__date=timezone.localtime(timezone.now()).date()
        )
        .annotate(truncated_date=TruncDate("read_at"))
        .exclude(
            # Skip existing days.
            truncated_date__in=DayStatistics.objects.all().values_list("day", flat=True)
        )
        .distinct()
        .order_by("truncated_date")
        .values_list("truncated_date", flat=True)
    )

    # Budget distinct and sorting.
    dates_to_generate = sorted(list(set(dates_to_generate)))

    print("Found {} day(s) to reconstruct".format(len(dates_to_generate)))

    for current_day in dates_to_generate:
        print(" - Reconstructing:", current_day)
        create_statistics(target_day=current_day)


def reconstruct_missing_day_statistics_by_hours() -> None:
    """Reconstructs missing day statistics by using available hour statistics."""
    dates_to_generate = (
        HourStatistics.objects.all()
        .annotate(truncated_date=TruncDate("hour_start"))
        .exclude(
            # Skip existing days.
            truncated_date__in=DayStatistics.objects.all().values_list("day", flat=True)
        )
        .order_by("truncated_date")
        .values_list("truncated_date", flat=True)
    )

    # Budget distinct and sorting.
    dates_to_generate = sorted(list(set(dates_to_generate)))

    print("Found {} day(s) to reconstruct".format(len(dates_to_generate)))

    for current_day in dates_to_generate:
        print(" - Reconstructing:", current_day)

        day_totals = HourStatistics.objects.filter(
            hour_start__date=current_day
        ).aggregate(
            electricity1_sum=Sum("electricity1"),
            electricity2_sum=Sum("electricity2"),
            electricity1_returned_sum=Sum("electricity1_returned"),
            electricity2_returned_sum=Sum("electricity2_returned"),
            gas_sum=Sum("gas"),
        )

        DayStatistics.objects.create(
            day=current_day,
            electricity1=day_totals["electricity1_sum"],
            electricity2=day_totals["electricity2_sum"],
            electricity1_returned=day_totals["electricity1_returned_sum"],
            electricity2_returned=day_totals["electricity2_returned_sum"],
            gas=day_totals["gas_sum"],
            total_cost=0,
            electricity1_cost=0,
            electricity2_cost=0,
        )
