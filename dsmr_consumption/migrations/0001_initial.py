# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ConsumptionSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compactor_grouping_type', models.IntegerField(verbose_name='Compactor grouping type', default=2, choices=[(1, 'By reading (every 10 seconds)'), (2, 'By minute')], help_text='Electricity readings are read every 10 seconds. We can group those for you.')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Consumption configuration',
            },
        ),

        migrations.CreateModel(
            name='ElectricityConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_at', models.DateTimeField(unique=True)),
                ('delivered_1', models.DecimalField(max_digits=9, decimal_places=3, help_text='Meter Reading electricity delivered to client (low tariff) in 0,001 kWh')),
                ('returned_1', models.DecimalField(max_digits=9, decimal_places=3, help_text='Meter Reading electricity delivered by client (low tariff) in 0,001 kWh')),
                ('delivered_2', models.DecimalField(max_digits=9, decimal_places=3, help_text='Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh')),
                ('returned_2', models.DecimalField(max_digits=9, decimal_places=3, help_text='Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh')),
                ('tariff', models.IntegerField(help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.')),
                ('currently_delivered', models.DecimalField(max_digits=9, decimal_places=3, help_text='Actual electricity power delivered (+P) in 1 Watt resolution')),
                ('currently_returned', models.DecimalField(max_digits=9, decimal_places=3, help_text='Actual electricity power received (-P) in 1 Watt resolution')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='EnergySupplierPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start', models.DateField(verbose_name='Start', help_text='Contract start')),
                ('end', models.DateField(null=True, verbose_name='End', blank=True, help_text='Contract end')),
                ('electricity_1_price', models.DecimalField(decimal_places=5, verbose_name='Electricity 1 price', default=0, max_digits=11)),
                ('electricity_2_price', models.DecimalField(decimal_places=5, verbose_name='Electricity 2 price', default=0, max_digits=11)),
                ('gas_price', models.DecimalField(decimal_places=5, verbose_name='Gas price', default=0, max_digits=11)),
                ('description', models.CharField(verbose_name='Description', null=True, max_length=255, blank=True, help_text='For your own reference, i.e. the name of your supplier')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Energy supplier price',
                'verbose_name_plural': 'Energy supplier prices',
            },
        ),
        migrations.CreateModel(
            name='GasConsumption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('read_at', models.DateTimeField(unique=True)),
                ('delivered', models.DecimalField(max_digits=9, decimal_places=3, help_text='Last hourly value delivered to client')),
                ('currently_delivered', models.DecimalField(max_digits=9, decimal_places=3, help_text='Actual value delivered to client, since the last hour')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.AlterUniqueTogether(
            name='energysupplierprice',
            unique_together=set([('start', 'end')]),
        ),
    ]
