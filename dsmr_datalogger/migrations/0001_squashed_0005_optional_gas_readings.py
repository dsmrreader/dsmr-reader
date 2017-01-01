# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def initialize_meter_statistics(apps, schema_editor):
    """ Guarantees there is at least one instance in the database, which will be updated later. """
    MeterStatistics = apps.get_model('dsmr_datalogger', 'MeterStatistics')

    # We can't (and shouldn't) use Solo here.
    MeterStatistics.objects.create()  # All fields are NULL in database, by design.
    assert MeterStatistics.objects.exists()


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataloggerSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('track', models.BooleanField(default=True, help_text='Whether we should track the P1 port on your smartmeter. Almost every feature inside this project requires this to be enabled. However, it might be disabled temporarily due to technical reasons, such as data migrations.', verbose_name='Poll P1 port')),
                ('baud_rate', models.IntegerField(default=115200, help_text='BAUD rate used for Smartmeter. 115200 for DSMR v4, 9600 for older versions', verbose_name='BAUD rate')),
                ('com_port', models.CharField(max_length=196, help_text='COM-port connected to Smartmeter.', default='/dev/ttyUSB0', verbose_name='COM-port')),
                ('track_meter_statistics', models.BooleanField(default=True, help_text='Whether we should track any extra statistics sent by the meter, such as the number of power failures of voltage dips. Data is not required for core features.', verbose_name='Track meter statistics')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Datalogger configuration',
            },
        ),
        migrations.CreateModel(
            name='DsmrReading',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField()),
                ('electricity_delivered_1', models.DecimalField(decimal_places=3, max_digits=9, help_text='Meter Reading electricity delivered to client (low tariff) in 0,001 kWh')),
                ('electricity_returned_1', models.DecimalField(decimal_places=3, max_digits=9, help_text='Meter Reading electricity delivered by client (low tariff) in 0,001 kWh')),
                ('electricity_delivered_2', models.DecimalField(decimal_places=3, max_digits=9, help_text='Meter Reading electricity delivered to client (normal tariff) in 0,001 kWh')),
                ('electricity_returned_2', models.DecimalField(decimal_places=3, max_digits=9, help_text='Meter Reading electricity delivered by client (normal tariff) in 0,001 kWh')),
                ('electricity_tariff', models.IntegerField(help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.')),
                ('electricity_currently_delivered', models.DecimalField(decimal_places=3, max_digits=9, help_text='Actual electricity power delivered (+P) in 1 Watt resolution')),
                ('electricity_currently_returned', models.DecimalField(decimal_places=3, max_digits=9, help_text='Actual electricity power received (-P) in 1 Watt resolution')),
                ('power_failure_count', models.IntegerField(help_text='Number of power failures in any phases')),
                ('long_power_failure_count', models.IntegerField(help_text='Number of long power failures in any phase')),
                ('voltage_sag_count_l1', models.IntegerField(help_text='Number of voltage sags/dips in phase L1')),
                ('voltage_sag_count_l2', models.IntegerField(help_text='Number of voltage sags/dips in phase L2 (polyphase meters only)')),
                ('voltage_sag_count_l3', models.IntegerField(help_text='Number of voltage sags/dips in phase L3 (polyphase meters only)')),
                ('voltage_swell_count_l1', models.IntegerField(help_text='Number of voltage swells in phase L1')),
                ('voltage_swell_count_l2', models.IntegerField(help_text='Number of voltage swells in phase L2 (polyphase meters only)')),
                ('voltage_swell_count_l3', models.IntegerField(help_text='Number of voltage swells in phase L3 (polyphase meters only)')),
                ('extra_device_timestamp', models.DateTimeField(help_text='Last hourly reading timestamp')),
                ('extra_device_delivered', models.DecimalField(decimal_places=3, max_digits=9, help_text='Last hourly value delivered to client')),
                ('processed', models.BooleanField(default=False, db_index=True, help_text='Whether this reading has been processed for merging into statistics')),
            ],
            options={
                'default_permissions': (),
                'ordering': ['timestamp'],
            },
        ),
        migrations.CreateModel(
            name='MeterStatistics',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now=True, help_text='Timestamp indicating when the reading was taken, according to the meter')),
                ('electricity_tariff', models.IntegerField(default=None, help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff  dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.', null=True)),
                ('power_failure_count', models.IntegerField(default=None, help_text='Number of power failures in any phases', null=True)),
                ('long_power_failure_count', models.IntegerField(default=None, help_text='Number of long power failures in any phase', null=True)),
                ('voltage_sag_count_l1', models.IntegerField(default=None, help_text='Number of voltage sags/dips in phase L1', null=True)),
                ('voltage_sag_count_l2', models.IntegerField(default=None, help_text='Number of voltage sags/dips in phase L2 (polyphase meters only)', null=True)),
                ('voltage_sag_count_l3', models.IntegerField(default=None, help_text='Number of voltage sags/dips in phase L3 (polyphase meters only)', null=True)),
                ('voltage_swell_count_l1', models.IntegerField(default=None, help_text='Number of voltage swells in phase L1', null=True)),
                ('voltage_swell_count_l2', models.IntegerField(default=None, help_text='Number of voltage swells in phase L2 (polyphase meters only)', null=True)),
                ('voltage_swell_count_l3', models.IntegerField(default=None, help_text='Number of voltage swells in phase L3 (polyphase meters only)', null=True)),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'DSMR Meter statistics',
            },
        ),
        migrations.RunPython(initialize_meter_statistics),
        migrations.AlterModelOptions(
            name='dsmrreading',
            options={'default_permissions': (), 'verbose_name': 'DSMR reading', 'ordering': ['timestamp']},
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='electricity_tariff',
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='long_power_failure_count',
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='power_failure_count',
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='voltage_sag_count_l1',
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='voltage_sag_count_l2',
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='voltage_sag_count_l3',
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='voltage_swell_count_l1',
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='voltage_swell_count_l2',
        ),
        migrations.RemoveField(
            model_name='dsmrreading',
            name='voltage_swell_count_l3',
        ),
        migrations.AlterField(
            model_name='dsmrreading',
            name='timestamp',
            field=models.DateTimeField(help_text='Timestamp indicating when the reading was taken, according to the meter'),
        ),
        migrations.RemoveField(
            model_name='dataloggersettings',
            name='baud_rate',
        ),
        migrations.AddField(
            model_name='dataloggersettings',
            name='dsmr_version',
            field=models.IntegerField(default=4, help_text='The DSMR version your meter supports. Version should be printed on meter.', verbose_name='DSMR version', choices=[(4, 'DSMR version 4'), (3, 'DSMR version 2/3')]),
        ),
        migrations.AlterField(
            model_name='dsmrreading',
            name='extra_device_delivered',
            field=models.DecimalField(decimal_places=3, default=None, help_text='Last hourly value delivered to client', null=True, max_digits=9),
        ),
        migrations.AlterField(
            model_name='dsmrreading',
            name='extra_device_timestamp',
            field=models.DateTimeField(default=None, help_text='Last hourly reading timestamp', null=True),
        ),
    ]
