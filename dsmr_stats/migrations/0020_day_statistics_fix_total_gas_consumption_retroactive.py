# Generated by Django 3.2.16 on 2023-01-05 23:16
import collections
from decimal import Decimal
from time import time, sleep

from django.db import migrations
from django.db.models import Sum
from django.utils import timezone


def regenerate_data(apps, schema_editor):
    """Try to fix any invalid gas data due to #1770."""
    DayStatistics = apps.get_model("dsmr_stats", "DayStatistics")
    HourStatistics = apps.get_model("dsmr_stats", "HourStatistics")
    Notification = apps.get_model("dsmr_frontend", "Notification")

    import dsmr_backend.services.backend

    if dsmr_backend.services.backend.is_recent_installation():
        # Skip for new installations.
        return

    # No DB index, but should be fine.
    days = DayStatistics.objects.all()
    day_count = days.count()
    x = 0
    total_difference_occurrences = 0
    total_gas_difference = Decimal(0)
    difference_occurrences_per_year = collections.defaultdict(int)
    total_difference_per_year = collections.defaultdict(Decimal)
    per_day_messages = []

    for current in days:
        x += 1
        print(
            "Data migration: Retroactively checking/recalculating gas consumption for day statistics: {} ({}/{})".format(
                current.day, x, day_count
            )
        )

        # Straight copy from create_daily_statistics()
        hours_in_day = dsmr_backend.services.backend.hours_in_day(day=current.day)
        start_of_day = timezone.make_aware(
            timezone.datetime(
                year=current.day.year,
                month=current.day.month,
                day=current.day.day,
                hour=0,
                minute=0,
            )
        )
        end_of_day = start_of_day + timezone.timedelta(hours=hours_in_day)
        hours_gas_sum = HourStatistics.objects.filter(
            hour_start__gte=start_of_day,
            hour_start__lt=end_of_day,
        ).aggregate(gas_sum=Sum("gas"),)["gas_sum"]

        if not hours_gas_sum or not current.gas:
            continue

        current_day_gas_diff = hours_gas_sum - current.gas

        # Only override when consumption is MORE
        if current_day_gas_diff > 0:
            output_message = f"{current.day} | Before: {current.gas} m³ - Recalculated: {hours_gas_sum} m³ | Difference: {current_day_gas_diff} m³"
            print(output_message)
            per_day_messages.append(output_message)

            total_gas_difference += current_day_gas_diff
            total_difference_occurrences += 1
            difference_occurrences_per_year[current.day.year] += 1
            total_difference_per_year[current.day.year] += current_day_gas_diff

            # Update day, prices will be recalculated below.
            current.gas = hours_gas_sum
            current.save()

    if total_difference_occurrences > 0:
        # Reflect changes for prices.
        import dsmr_stats.services

        dsmr_stats.services.recalculate_prices()

        total_text = "DSMR-reader found and fixed historic gas differences in favor of issue #1770. Note that the number format is English and not localized.\n"

        total_text += f"\nDifferences by year ({total_gas_difference} m³ in total):\n"
        for year, total in total_difference_per_year.items():
            total_text += f"{year} | {total} m³\n"

        total_text += (
            f"\nOccurrences by year ({total_difference_occurrences} x in total):\n"
        )
        for year, count in difference_occurrences_per_year.items():
            total_text += f"{year} | {count} x\n"

        print(total_text)

        # Total
        Notification.objects.create(message=total_text)
        # Per-day
        per_day_messages.insert(
            0,
            "Any per-day differences in favor of issue #1770 are displayed below. Note that the number format is English and not localized.\n",
        )
        Notification.objects.create(message="\n".join(per_day_messages))

        print(
            "The information above should also be logged as notifications, accessible on the Dashboard page of DSMR-reader."
        )


def noop(apps, schema_editor):
    """Cannot revert."""
    pass


class Migration(migrations.Migration):
    operations = [migrations.RunPython(regenerate_data, noop)]

    dependencies = [
        ("dsmr_stats", "0019_day_statistics_meter_position_timestamps_retroactive"),
    ]
