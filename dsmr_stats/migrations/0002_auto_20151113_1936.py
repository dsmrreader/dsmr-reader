# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ElectricityConsumption',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('read_at', models.DateTimeField()),
                ('delivered_1', models.DecimalField(help_text='Meter Reading electricity delivered to client (low tariff) in 0,001 kWh', decimal_places=3, max_digits=9)),
                ('returned_1', models.DecimalField(help_text='Meter Reading electricity delivered by client (low tariff) in 0,001 kWh', decimal_places=3, max_digits=9)),
                ('delivered_2', models.DecimalField(help_text='Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh', decimal_places=3, max_digits=9)),
                ('returned_2', models.DecimalField(help_text='Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh', decimal_places=3, max_digits=9)),
                ('tariff', models.IntegerField(help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.')),
                ('currently_delivered', models.DecimalField(help_text='Actual electricity power delivered (+P) in 1 Watt resolution', decimal_places=3, max_digits=9)),
                ('currently_returned', models.DecimalField(help_text='Actual electricity power received (-P) in 1 Watt resolution', decimal_places=3, max_digits=9)),
            ],
        ),
        migrations.CreateModel(
            name='ElectricityStatistics',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('day', models.DateField()),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('read_at', models.DateTimeField()),
                ('delivered', models.DecimalField(help_text='Last hourly value delivered to client', decimal_places=3, max_digits=9)),
                ('currently_delivered', models.DecimalField(help_text='Actual value delivered to client, since the last hour', decimal_places=3, max_digits=9)),
            ],
        ),
        migrations.AddField(
            model_name='dsmrreading',
            name='processed',
            field=models.BooleanField(help_text='Whether this reading has been processed for individual splitting', db_index=True, default=False),
        ),
    ]
