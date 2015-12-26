# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0001_renamed_migrations'),
        ('dsmr_stats', '0002_consumption_models'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dsmrreading',
            options={'ordering': ['timestamp']},
        ),
        migrations.AlterField(
            model_name='electricityconsumption',
            name='read_at',
            field=models.DateTimeField(unique=True),
        ),
        migrations.AlterField(
            model_name='electricitystatistics',
            name='day',
            field=models.DateField(unique=True),
        ),
        migrations.AlterField(
            model_name='gasconsumption',
            name='read_at',
            field=models.DateTimeField(unique=True),
        ),
    ]
