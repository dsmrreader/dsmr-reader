# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0007_min_max_temperature_statistics_retroactive'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='daystatistics',
            options={'verbose_name': 'Day statistics (read only)', 'default_permissions': (), 'verbose_name_plural': 'Day statistics (read only)'},
        ),
        migrations.AlterModelOptions(
            name='hourstatistics',
            options={'verbose_name': 'Hour statistics (read only)', 'default_permissions': (), 'verbose_name_plural': 'Hour statistics (read only)'},
        ),
    ]
