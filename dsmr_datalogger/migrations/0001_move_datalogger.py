# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataloggerSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('baud_rate', models.IntegerField(verbose_name='BAUD rate', help_text='BAUD rate used for Smartmeter. 115200 for DSMR v4, 9600 for older versions', default=115200)),
                ('com_port', models.CharField(verbose_name='COM-port', help_text='COM-port connected to Smartmeter.', max_length=196, default='/dev/ttyUSB0')),
            ],
            options={
                'verbose_name': 'Datalogger configuration',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='DsmrReading',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('electricity_delivered_1', models.DecimalField(help_text='Meter Reading electricity delivered to client (low tariff) in 0,001 kWh', max_digits=9, decimal_places=3)),
                ('electricity_returned_1', models.DecimalField(help_text='Meter Reading electricity delivered by client (low tariff) in 0,001 kWh', max_digits=9, decimal_places=3)),
                ('electricity_delivered_2', models.DecimalField(help_text='Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh', max_digits=9, decimal_places=3)),
                ('electricity_returned_2', models.DecimalField(help_text='Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh', max_digits=9, decimal_places=3)),
                ('electricity_tariff', models.IntegerField(help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.')),
                ('electricity_currently_delivered', models.DecimalField(help_text='Actual electricity power delivered (+P) in 1 Watt resolution', max_digits=9, decimal_places=3)),
                ('electricity_currently_returned', models.DecimalField(help_text='Actual electricity power received (-P) in 1 Watt resolution', max_digits=9, decimal_places=3)),
                ('power_failure_count', models.IntegerField(help_text='Number of power failures in any phases')),
                ('long_power_failure_count', models.IntegerField(help_text='Number of long power failures in any phase')),
                ('voltage_sag_count_l1', models.IntegerField(help_text='Number of voltage sags/dips in phase L1')),
                ('voltage_sag_count_l2', models.IntegerField(help_text='Number of voltage sags/dips in phase L2 (polyphase meters only)')),
                ('voltage_sag_count_l3', models.IntegerField(help_text='Number of voltage sags/dips in phase L3 (polyphase meters only)')),
                ('voltage_swell_count_l1', models.IntegerField(help_text='Number of voltage swells in phase L1')),
                ('voltage_swell_count_l2', models.IntegerField(help_text='Number of voltage swells in phase L2 (polyphase meters only)')),
                ('voltage_swell_count_l3', models.IntegerField(help_text='Number of voltage swells in phase L3 (polyphase meters only)')),
                ('extra_device_timestamp', models.DateTimeField(help_text='Last hourly reading timestamp')),
                ('extra_device_delivered', models.DecimalField(help_text='Last hourly value delivered to client', max_digits=9, decimal_places=3)),
                ('processed', models.BooleanField(help_text='Whether this reading has been processed for merging into statistics', db_index=True, default=False)),
            ],
            options={
                'default_permissions': (),
                'ordering': ['timestamp'],
            },
        ),
    ]
