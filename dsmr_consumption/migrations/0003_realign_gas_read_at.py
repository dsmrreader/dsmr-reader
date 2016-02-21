# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db import migrations, models

import dsmr_stats.services


def realign_forwards(apps, schema_editor):
    """ Fetches all existing gas consumption readings and realigns them by changing read_at. """
    realign_gas_readings(apps, schema_editor, hours_offset=-1)


def realign_backwards(apps, schema_editor):
    """ Same as above, but reversed. """
    realign_gas_readings(apps, schema_editor, hours_offset=+1)


def realign_gas_readings(apps, schema_editor, hours_offset):
    """ Alters the read_at value by the offset given and purges all existing statistics. """
    # We use F() to have the database sort things out.
    GasConsumption = apps.get_model('dsmr_consumption', 'GasConsumption')
    print('Updating gas consumptions ({} records) with hour offset: {}'.format(
        GasConsumption.objects.all().count(), hours_offset
    ))
    GasConsumption.objects.all().update(
        read_at=models.F('read_at') + timezone.timedelta(hours=hours_offset)
    )

    # We have to recalculate ALL trends and statistics generated.
    DayStatistics = apps.get_model('dsmr_stats', 'DayStatistics')
    HourStatistics = apps.get_model('dsmr_stats', 'HourStatistics')
    day_statistics_count = DayStatistics.objects.all().count()
    print('Purging existing day ({} records) & hour statistics ({} records)'.format(
        day_statistics_count, HourStatistics.objects.all().count()
    ))
    DayStatistics.objects.all().delete()
    HourStatistics.objects.all().delete()

    for counter in range(1, day_statistics_count + 1):
        print(" --- Regenerating daily/hourly statistics for day {} of {}".format(counter, day_statistics_count))
        dsmr_stats.services.analyze()


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_consumption', '0002_split_dsmr_reading_fields'),
        ('dsmr_stats', '0015_trend_statistics_model'),
    ]

    operations = [
        migrations.RunPython(realign_forwards, realign_backwards),
    ]
