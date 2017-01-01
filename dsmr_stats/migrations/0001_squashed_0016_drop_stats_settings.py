# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_weather', '0001_weather_models'),
        ('dsmr_frontend', '0001_initial'),
        ('dsmr_datalogger', '0001_squashed_0005_optional_gas_readings'),
        ('dsmr_consumption', '0001_squashed_0004_recalculate_gas_consumption'),
    ]

    operations = [
        migrations.CreateModel(
            name='DsmrReading',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('electricity_delivered_1', models.DecimalField(decimal_places=3, help_text='Meter Reading electricity delivered to client (low tariff) in 0,001 kWh', max_digits=9)),
                ('electricity_returned_1', models.DecimalField(decimal_places=3, help_text='Meter Reading electricity delivered by client (low tariff) in 0,001 kWh', max_digits=9)),
                ('electricity_delivered_2', models.DecimalField(decimal_places=3, help_text='Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh', max_digits=9)),
                ('electricity_returned_2', models.DecimalField(decimal_places=3, help_text='Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh', max_digits=9)),
                ('electricity_tariff', models.IntegerField(help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.')),
                ('electricity_currently_delivered', models.DecimalField(decimal_places=3, help_text='Actual electricity power delivered (+P) in 1 Watt resolution', max_digits=9)),
                ('electricity_currently_returned', models.DecimalField(decimal_places=3, help_text='Actual electricity power received (-P) in 1 Watt resolution', max_digits=9)),
                ('power_failure_count', models.IntegerField(help_text='Number of power failures in any phases')),
                ('long_power_failure_count', models.IntegerField(help_text='Number of long power failures in any phase')),
                ('voltage_sag_count_l1', models.IntegerField(help_text='Number of voltage sags/dips in phase L1')),
                ('voltage_sag_count_l2', models.IntegerField(help_text='Number of voltage sags/dips in phase L2 (polyphase meters only)')),
                ('voltage_sag_count_l3', models.IntegerField(help_text='Number of voltage sags/dips in phase L3 (polyphase meters only)')),
                ('voltage_swell_count_l1', models.IntegerField(help_text='Number of voltage swells in phase L1')),
                ('voltage_swell_count_l2', models.IntegerField(help_text='Number of voltage swells in phase L2 (polyphase meters only)')),
                ('voltage_swell_count_l3', models.IntegerField(help_text='Number of voltage swells in phase L3 (polyphase meters only)')),
                ('extra_device_timestamp', models.DateTimeField(help_text='Last hourly reading timestamp')),
                ('extra_device_delivered', models.DecimalField(decimal_places=3, help_text='Last hourly value delivered to client', max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='ElectricityConsumption',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('read_at', models.DateTimeField(unique=True)),
                ('delivered_1', models.DecimalField(decimal_places=3, help_text='Meter Reading electricity delivered to client (low tariff) in 0,001 kWh', max_digits=9)),
                ('returned_1', models.DecimalField(decimal_places=3, help_text='Meter Reading electricity delivered by client (low tariff) in 0,001 kWh', max_digits=9)),
                ('delivered_2', models.DecimalField(decimal_places=3, help_text='Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh', max_digits=9)),
                ('returned_2', models.DecimalField(decimal_places=3, help_text='Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh', max_digits=9)),
                ('tariff', models.IntegerField(help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.')),
                ('currently_delivered', models.DecimalField(decimal_places=3, help_text='Actual electricity power delivered (+P) in 1 Watt resolution', max_digits=9)),
                ('currently_returned', models.DecimalField(decimal_places=3, help_text='Actual electricity power received (-P) in 1 Watt resolution', max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='ElectricityStatistics',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('day', models.DateField(unique=True)),
                ('power_failure_count', models.IntegerField(help_text='Number of power failures in any phases')),
                ('long_power_failure_count', models.IntegerField(help_text='Number of long power failures in any phase')),
                ('voltage_sag_count_l1', models.IntegerField(help_text='Number of voltage sags/dips in phase L1')),
                ('voltage_sag_count_l2', models.IntegerField(help_text='Number of voltage sags/dips in phase L2 (polyphase meters only)')),
                ('voltage_sag_count_l3', models.IntegerField(help_text='Number of voltage sags/dips in phase L3 (polyphase meters only)')),
                ('voltage_swell_count_l1', models.IntegerField(help_text='Number of voltage swells in phase L1')),
                ('voltage_swell_count_l2', models.IntegerField(help_text='Number of voltage swells in phase L2 (polyphase meters only)')),
                ('voltage_swell_count_l3', models.IntegerField(help_text='Number of voltage swells in phase L3 (polyphase meters only)')),
            ],
        ),
        migrations.CreateModel(
            name='GasConsumption',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('read_at', models.DateTimeField(unique=True)),
                ('delivered', models.DecimalField(decimal_places=3, help_text='Last hourly value delivered to client', max_digits=9)),
                ('currently_delivered', models.DecimalField(decimal_places=3, help_text='Actual value delivered to client, since the last hour', max_digits=9)),
            ],
        ),
        migrations.AddField(
            model_name='dsmrreading',
            name='processed',
            # Django bug? Manually removed 'db_index=True' to prevent migrations fro m crashing.
            field=models.BooleanField(default=False, help_text='Whether this reading has been processed for individual splitting'),
        ),
        migrations.AlterModelOptions(
            name='dsmrreading',
            options={'ordering': ['timestamp']},
        ),
        migrations.CreateModel(
            name='EnergySupplierPrice',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('start', models.DateField()),
                ('end', models.DateField(blank=True, null=True)),
                ('electricity_1_price', models.DecimalField(decimal_places=5, max_digits=11)),
                ('electricity_2_price', models.DecimalField(decimal_places=5, max_digits=11)),
                ('gas_price', models.DecimalField(decimal_places=5, max_digits=11)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='energysupplierprice',
            unique_together=set([('start', 'end')]),
        ),
        migrations.AddField(
            model_name='energysupplierprice',
            name='description',
            field=models.CharField(null=True, max_length=255, help_text='For your own reference, i.e. your supplier name', blank=True),
        ),
        migrations.AlterField(
            model_name='energysupplierprice',
            name='electricity_1_price',
            field=models.DecimalField(default=0, decimal_places=5, max_digits=11),
        ),
        migrations.AlterField(
            model_name='energysupplierprice',
            name='electricity_2_price',
            field=models.DecimalField(default=0, decimal_places=5, max_digits=11),
        ),
        migrations.AlterField(
            model_name='energysupplierprice',
            name='gas_price',
            field=models.DecimalField(default=0, decimal_places=5, max_digits=11),
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('day', models.DateField()),
                ('description', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name_plural': 'Notes',
                'verbose_name': 'Note',
            },
        ),
        migrations.CreateModel(
            name='StatsSettings',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('compactor_grouping_type', models.IntegerField(default=2, help_text='Electricity readings are read every 10 seconds. We can group those for you.', choices=[(1, 'By reading (every 10 seconds)'), (2, 'By minute')], verbose_name='Compactor grouping type')),
                ('reverse_dashboard_graphs', models.BooleanField(default=False, help_text='Whether graphs are rendered with an reversed X-axis.', verbose_name='Reverse dashboard graphs')),
            ],
            options={
                'verbose_name': 'Stats configuration',
            },
        ),
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
        migrations.AlterModelOptions(
            name='electricitystatistics',
            options={'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='note',
            options={'verbose_name_plural': 'Notes', 'verbose_name': 'Note', 'default_permissions': ()},
        ),
        migrations.AlterField(
            model_name='note',
            name='day',
            field=models.DateField(verbose_name='Day'),
        ),
        migrations.AlterField(
            model_name='note',
            name='description',
            field=models.CharField(max_length=256, verbose_name='Description'),
        ),
        migrations.DeleteModel(
            name='ElectricityStatistics',
        ),
        migrations.CreateModel(
            name='StatsSettings',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('track', models.BooleanField(default=True, help_text='Whether we should track trends by storing daily consumption summaries.', verbose_name='Track trends')),
            ],
            options={
                'verbose_name': 'Trends & statistics configuration',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='DayStatistics',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('day', models.DateField(unique=True)),
                ('total_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('electricity1', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity2', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity1_returned', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity2_returned', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity1_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('electricity2_cost', models.DecimalField(decimal_places=2, max_digits=8)),
                ('gas', models.DecimalField(default=None, decimal_places=3, null=True, max_digits=9)),
                ('gas_cost', models.DecimalField(default=None, decimal_places=2, null=True, max_digits=8)),
                ('average_temperature', models.DecimalField(default=None, decimal_places=1, null=True, max_digits=4)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='HourStatistics',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('hour_start', models.DateTimeField(unique=True)),
                ('electricity1', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity2', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity1_returned', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity2_returned', models.DecimalField(decimal_places=3, max_digits=9)),
                ('gas', models.DecimalField(default=None, decimal_places=3, null=True, max_digits=9)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.DeleteModel(
            name='StatsSettings',
        ),
    ]
