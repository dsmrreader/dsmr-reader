# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_datalogger', '0001_squashed_0005_optional_gas_readings'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dsmrreading',
            options={'verbose_name': 'DSMR reading (read only)', 'default_permissions': (), 'ordering': ['timestamp'], 'verbose_name_plural': 'DSMR readings (read only)'},
        ),
        migrations.AlterModelOptions(
            name='meterstatistics',
            options={'verbose_name': 'DSMR Meter statistics (read only)', 'default_permissions': (), 'verbose_name_plural': 'DSMR Meter statistics (read only)'},
        ),
    ]
