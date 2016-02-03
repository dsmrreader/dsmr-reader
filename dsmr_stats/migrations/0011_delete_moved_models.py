# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0010_split_models_among_apps'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DsmrReading',
        ),
        migrations.DeleteModel(
            name='ElectricityConsumption',
        ),
        migrations.DeleteModel(
            name='EnergySupplierPrice',
        ),
        migrations.DeleteModel(
            name='GasConsumption',
        ),
        migrations.DeleteModel(
            name='StatsSettings',
        ),
    ]
