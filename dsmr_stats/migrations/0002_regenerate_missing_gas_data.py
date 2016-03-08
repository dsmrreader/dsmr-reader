# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import time

from django.db import migrations
from django.utils import timezone


def regenerate_missing_data(apps, schema_editor):
    GasConsumption = apps.get_model('dsmr_consumption', 'GasConsumption')
    HourStatistics = apps.get_model('dsmr_stats', 'HourStatistics')
    DayStatistics = apps.get_model('dsmr_stats', 'DayStatistics')

    print('')

    # Skip when there were no gas readings at all.
    if not GasConsumption.objects.exists():
        print('--- No data regeneration required')
        return

    try:
        # Check for any missing gas data.
        first_missing_gas_stat = HourStatistics.objects.filter(
            gas__isnull=True,
            hour_start__gte=timezone.make_aware(timezone.datetime(2016, 1, 1, 12))
        ).order_by('hour_start')[0]
    except IndexError:
        return

    target_hour = timezone.localtime(first_missing_gas_stat.hour_start)
    day_start = timezone.make_aware(timezone.datetime.combine(target_hour, time.min))
    print('Deleting statistics starting from: {}'.format(day_start))

    HourStatistics.objects.filter(hour_start__gte=day_start).delete()
    DayStatistics.objects.filter(day__gte=day_start.date()).delete()

    days_diff = (timezone.now() - day_start).days
    import dsmr_stats.services

    for x in range(1, days_diff + 1):
        # Just call analyze for each day. If we missed a day or so, the backend will regenerate it.
        print('Regenerating day: {} / {}'.format(x, days_diff))
        dsmr_stats.services.analyze()


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0001_squashed_0016_drop_stats_settings'),
    ]

    operations = [
        migrations.RunPython(regenerate_missing_data)
    ]
