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
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('day', models.DateField(unique=True)),
                ('electricity1', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity2_returned', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity1_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('electricity2_cost', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='GasStatistics',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('day', models.DateField(unique=True)),
                ('gas', models.DecimalField(decimal_places=3, max_digits=9)),
                ('gas_cost', models.DecimalField(decimal_places=2, max_digits=8)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='StatsSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('track', models.BooleanField(help_text='Whether we should track trends by storing daily consumption summaries.', verbose_name='Track trends', default=True)),
            ],
            options={
                'verbose_name': 'Statistics configuration',
                'default_permissions': (),
            },
        ),
    ]
