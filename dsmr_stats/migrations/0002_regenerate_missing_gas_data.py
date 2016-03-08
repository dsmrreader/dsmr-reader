# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils import timezone


def regenerate_missing_data(apps, schema_editor):
    import dsmr_stats.services
    GasConsumption = apps.get_model('dsmr_consumption', 'GasConsumption')

    # Skip when there were no gas readings at all.
    if not GasConsumption.objects.exists():
        return

    # Check for any missing gas data.
    HourStatistics = apps.get_model('dsmr_stats', 'HourStatistics')
    missing_gas_hours = HourStatistics.objects.filter(
        gas__isnull=True,
        hour_start__gte=timezone.make_aware(timezone.datetime(2016, 1, 1, 12))
    ).order_by('hour_start')

    days_to_regenerate = []

    for current_hour_stats in missing_gas_hours:
        # Regeneration MUST be in local time.
        current_hour = timezone.localtime(current_hour_stats.hour_start)
        print('Deleting and regenerating hour statistiscs: {}'.format(current_hour))

        current_hour_stats.delete()
        dsmr_stats.services.create_hourly_statistics(day=current_hour.date(), hour=current_hour.hour)
        days_to_regenerate.append(current_hour.date())

    # Unique days.
    days_to_regenerate = list(set(days_to_regenerate))
    DayStatistics = apps.get_model('dsmr_stats', 'DayStatistics')

    for current_day in days_to_regenerate:
        print('Deleting and regenerating daystatistics: {}'.format(current_day))

        DayStatistics.objects.filter(day=current_day).delete()
        dsmr_stats.services.create_daily_statistics(day=current_day)


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0001_squashed_0016_drop_stats_settings'),
    ]

    operations = [
        migrations.RunPython(regenerate_missing_data)
    ]
