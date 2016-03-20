# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def data_migration(apps, schema_editor):
    """ alters the (default) NULL values of gas hourly statistics to zero. """
    HourStatistics = apps.get_model('dsmr_stats', 'HourStatistics')
    HourStatistics.objects.filter(gas__isnull=True).update(gas=0)


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0003_hour_statistics_gas_default'),
    ]

    operations = [
        migrations.RunPython(data_migration),
    ]
