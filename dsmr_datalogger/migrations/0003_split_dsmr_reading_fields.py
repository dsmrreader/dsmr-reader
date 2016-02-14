# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def initial_meter_statistics(apps, schema_editor):
    """ Guarantees there is at least one instance in the database, which will be updated later. """
    MeterStatistics = apps.get_model('dsmr_datalogger', 'MeterStatistics')
    DsmrReading = apps.get_model('dsmr_datalogger', 'DsmrReading')

    # We can't (and shouldn't) use Solo here.
    stats = MeterStatistics.objects.create()  # All fields are NULL in database, by design.
    assert MeterStatistics.objects.exists()

    try:
        # Just use the latest DSMR reading, if any.
        latest_reading = DsmrReading.objects.all().order_by('-timestamp')[0]
    except IndexError:
        return

    stats.electricity_tariff = latest_reading.electricity_tariff
    stats.power_failure_count = latest_reading.power_failure_count
    stats.long_power_failure_count = latest_reading.long_power_failure_count
    stats.voltage_sag_count_l1 = latest_reading.voltage_sag_count_l1
    stats.voltage_sag_count_l2 = latest_reading.voltage_sag_count_l2
    stats.voltage_sag_count_l3 = latest_reading.voltage_sag_count_l3
    stats.voltage_swell_count_l1 = latest_reading.voltage_swell_count_l1
    stats.voltage_swell_count_l2 = latest_reading.voltage_swell_count_l2
    stats.voltage_swell_count_l3 = latest_reading.voltage_swell_count_l3
    stats.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_datalogger', '0002_add_meter_statistics'),
        # Just to make sure any pending data migrations and statistics generation are completed.
        ('dsmr_stats', '0015_trend_statistics_model'),
    ]

    operations = [
        migrations.RunPython(initial_meter_statistics),
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
    ]
