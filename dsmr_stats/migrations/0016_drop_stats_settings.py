# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0015_trend_statistics_model'),
    ]

    operations = [
        migrations.DeleteModel(
            name='StatsSettings',
        ),
    ]
