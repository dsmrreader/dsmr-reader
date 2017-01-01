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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('compactor_grouping_type', models.IntegerField(help_text='Electricity readings are read every 10 seconds. We can group those for you.', choices=[(1, 'By reading (every 10 seconds)'), (2, 'By minute')], verbose_name='Compactor grouping type', default=2)),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Consumption configuration',
            },
        ),
        migrations.CreateModel(
            name='ElectricityConsumption',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('read_at', models.DateTimeField(unique=True)),
                ('delivered_1', models.DecimalField(help_text='Meter Reading electricity delivered to client (low tariff) in 0,001 kWh', max_digits=9, decimal_places=3)),
                ('returned_1', models.DecimalField(help_text='Meter Reading electricity delivered by client (low tariff) in 0,001 kWh', max_digits=9, decimal_places=3)),
                ('delivered_2', models.DecimalField(help_text='Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh', max_digits=9, decimal_places=3)),
                ('returned_2', models.DecimalField(help_text='Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh', max_digits=9, decimal_places=3)),
                ('currently_delivered', models.DecimalField(help_text='Actual electricity power delivered (+P) in 1 Watt resolution', max_digits=9, decimal_places=3)),
                ('currently_returned', models.DecimalField(help_text='Actual electricity power received (-P) in 1 Watt resolution', max_digits=9, decimal_places=3)),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='EnergySupplierPrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('start', models.DateField(help_text='Contract start', verbose_name='Start')),
                ('end', models.DateField(help_text='Contract end', null=True, verbose_name='End', blank=True)),
                ('electricity_1_price', models.DecimalField(decimal_places=5, verbose_name='Electricity 1 price', default=0, max_digits=11)),
                ('electricity_2_price', models.DecimalField(decimal_places=5, verbose_name='Electricity 2 price', default=0, max_digits=11)),
                ('gas_price', models.DecimalField(decimal_places=5, verbose_name='Gas price', default=0, max_digits=11)),
                ('description', models.CharField(help_text='For your own reference, i.e. the name of your supplier', max_length=255, null=True, verbose_name='Description', blank=True)),
            ],
            options={
                'default_permissions': (),
                'verbose_name_plural': 'Energy supplier prices',
                'verbose_name': 'Energy supplier price',
            },
        ),
        migrations.CreateModel(
            name='GasConsumption',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('read_at', models.DateTimeField(unique=True)),
                ('delivered', models.DecimalField(help_text='Last hourly value delivered to client', max_digits=9, decimal_places=3)),
                ('currently_delivered', models.DecimalField(help_text='Actual value delivered to client, since the last hour', max_digits=9, decimal_places=3)),
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
