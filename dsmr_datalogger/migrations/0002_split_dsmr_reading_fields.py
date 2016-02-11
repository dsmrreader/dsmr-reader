# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def initial_meter_statistics(apps, schema_editor):
    """ Guarantees there is at least one instance in the database, which will be updated later. """
    MeterStatistics = apps.get_model('dsmr_datalogger', 'MeterStatistics')
    # We can't (and shouldn't) use Solo here.
    MeterStatistics.objects.create()  # All fields are NULL in database, by design.
    assert MeterStatistics.objects.exists()


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_datalogger', '0001_initial'),
        # Just to make sure any pending data migrations and statistics generation are completed.
        ('dsmr_stats', '0015_trend_statistics_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeterStatistics',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('timestamp', models.DateTimeField(help_text='Timestamp indicating when the reading was taken, according to the meter', auto_now=True)),
                ('electricity_tariff', models.IntegerField(help_text='Tariff indicator electricity. The tariff indicator can be used to switch tariff  dependent loads e.g boilers. This is responsibility of the P1 user. Note: Tariff code 1 is used for low tariff and tariff code 2 is used for normal tariff.', default=None, null=True)),
                ('power_failure_count', models.IntegerField(help_text='Number of power failures in any phases', default=None, null=True)),
                ('long_power_failure_count', models.IntegerField(help_text='Number of long power failures in any phase', default=None, null=True)),
                ('voltage_sag_count_l1', models.IntegerField(help_text='Number of voltage sags/dips in phase L1', default=None, null=True)),
                ('voltage_sag_count_l2', models.IntegerField(help_text='Number of voltage sags/dips in phase L2 (polyphase meters only)', default=None, null=True)),
                ('voltage_sag_count_l3', models.IntegerField(help_text='Number of voltage sags/dips in phase L3 (polyphase meters only)', default=None, null=True)),
                ('voltage_swell_count_l1', models.IntegerField(help_text='Number of voltage swells in phase L1', default=None, null=True)),
                ('voltage_swell_count_l2', models.IntegerField(help_text='Number of voltage swells in phase L2 (polyphase meters only)', default=None, null=True)),
                ('voltage_swell_count_l3', models.IntegerField(help_text='Number of voltage swells in phase L3 (polyphase meters only)', default=None, null=True)),
            ],
            options={
                'verbose_name': 'DSMR Meter statistics',
                'default_permissions': (),
            },
        ),
        migrations.AlterModelOptions(
            name='dsmrreading',
            options={'verbose_name': 'DSMR reading', 'default_permissions': (), 'ordering': ['timestamp']},
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
        migrations.AddField(
            model_name='dataloggersettings',
            name='track_meter_statistics',
            field=models.BooleanField(default=True, verbose_name='Track meter statistics', help_text='Whether we should track any extra statistics sent by the meter, such as the number of power failures of voltage dips. Data is not required for core features.'),
        ),
        migrations.RunPython(initial_meter_statistics),
    ]
