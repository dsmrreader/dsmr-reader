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
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('track', models.BooleanField(default=True, verbose_name='Poll P1 port', help_text='Whether we should track the P1 port on your smartmeter. Almost every feature inside this project requires this to be enabled. However, it might be disabled temporarily due to technical reasons, such as data migrations.')),
                ('baud_rate', models.IntegerField(default=115200, verbose_name='BAUD rate', help_text='BAUD rate used for Smartmeter. 115200 for DSMR v4, 9600 for older versions')),
                ('com_port', models.CharField(default='/dev/ttyUSB0', max_length=196, verbose_name='COM-port', help_text='COM-port connected to Smartmeter.')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Datalogger configuration',
            },
        ),
        migrations.CreateModel(
            name='DsmrReading',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('electricity_delivered_1', models.DecimalField(max_digits=9, decimal_places=3, help_text='Meter Reading electricity delivered to client (low tariff) in 0,001 kWh')),
                ('electricity_returned_1', models.DecimalField(max_digits=9, decimal_places=3, help_text='Meter Reading electricity delivered by client (low tariff) in 0,001 kWh')),
                ('electricity_delivered_2', models.DecimalField(max_digits=9, decimal_places=3, help_text='Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh')),
                ('electricity_returned_2', models.DecimalField(max_digits=9, decimal_places=3, help_text='Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh')),
                ('electricity_tariff', models.IntegerField(help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.')),
                ('electricity_currently_delivered', models.DecimalField(max_digits=9, decimal_places=3, help_text='Actual electricity power delivered (+P) in 1 Watt resolution')),
                ('electricity_currently_returned', models.DecimalField(max_digits=9, decimal_places=3, help_text='Actual electricity power received (-P) in 1 Watt resolution')),
                ('power_failure_count', models.IntegerField(help_text='Number of power failures in any phases')),
                ('long_power_failure_count', models.IntegerField(help_text='Number of long power failures in any phase')),
                ('voltage_sag_count_l1', models.IntegerField(help_text='Number of voltage sags/dips in phase L1')),
                ('voltage_sag_count_l2', models.IntegerField(help_text='Number of voltage sags/dips in phase L2 (polyphase meters only)')),
                ('voltage_sag_count_l3', models.IntegerField(help_text='Number of voltage sags/dips in phase L3 (polyphase meters only)')),
                ('voltage_swell_count_l1', models.IntegerField(help_text='Number of voltage swells in phase L1')),
                ('voltage_swell_count_l2', models.IntegerField(help_text='Number of voltage swells in phase L2 (polyphase meters only)')),
                ('voltage_swell_count_l3', models.IntegerField(help_text='Number of voltage swells in phase L3 (polyphase meters only)')),
                ('extra_device_timestamp', models.DateTimeField(help_text='Last hourly reading timestamp')),
                ('extra_device_delivered', models.DecimalField(max_digits=9, decimal_places=3, help_text='Last hourly value delivered to client')),
                ('processed', models.BooleanField(default=False, db_index=True, help_text='Whether this reading has been processed for merging into statistics')),
            ],
            options={
                'default_permissions': (),
                'ordering': ['timestamp'],
            },
        ),
    ]
