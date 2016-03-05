# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db import migrations, models

import dsmr_stats.services


def realign_gas_readings(apps, schema_editor):
    """ Alters the read_at value by the offset given and purges all existing statistics. """
    # We use F() to have the database sort things out.
    GasConsumption = apps.get_model('dsmr_consumption', 'GasConsumption')
    GasConsumption.objects.all().update(
        read_at=models.F('read_at') - timezone.timedelta(hours=1)
    )

    # We have to recalculate ALL trends and statistics generated.
    DayStatistics = apps.get_model('dsmr_stats', 'DayStatistics')
    HourStatistics = apps.get_model('dsmr_stats', 'HourStatistics')
    day_statistics_count = DayStatistics.objects.all().count()
    DayStatistics.objects.all().delete()
    HourStatistics.objects.all().delete()

    for counter in range(1, day_statistics_count + 1):
        dsmr_stats.services.analyze()


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_consumption', '0002_split_dsmr_reading_fields'),
        ('dsmr_stats', '0015_trend_statistics_model'),
    ]

    operations = [
        migrations.RunPython(realign_gas_readings),
    ]
