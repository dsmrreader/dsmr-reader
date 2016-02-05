# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0013_drop_old_statistics_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElectricityStatistics',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('day', models.DateField(unique=True)),
                ('electricity1', models.DecimalField(max_digits=9, decimal_places=3)),
                ('electricity2', models.DecimalField(max_digits=9, decimal_places=3)),
                ('electricity1_returned', models.DecimalField(max_digits=9, decimal_places=3)),
                ('electricity2_returned', models.DecimalField(max_digits=9, decimal_places=3)),
                ('electricity1_cost', models.DecimalField(max_digits=8, decimal_places=2)),
                ('electricity2_cost', models.DecimalField(max_digits=8, decimal_places=2)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='GasStatistics',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('day', models.DateField(unique=True)),
                ('gas', models.DecimalField(max_digits=9, decimal_places=3)),
                ('gas_cost', models.DecimalField(max_digits=8, decimal_places=2)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='StatsSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('track', models.BooleanField(default=True, help_text='Whether we should track trends by storing daily consumption summaries.', verbose_name='Track trends')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Statistics configuration',
            },
        ),
    ]
