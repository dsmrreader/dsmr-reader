# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

import dsmr_stats.services


def recalculate_statistics(apps, schema_editor):
    """ The previous migration purged al legacy statistics, so make sure to regenerate them. """
    ElectricityConsumption = apps.get_model('dsmr_consumption', 'ElectricityConsumption')
    ec_dates = ElectricityConsumption.objects.all().values_list('read_at', flat=True)

    if not ec_dates.exists():
        # Empty projects shouldn't care.
        return

    first_consumption = ec_dates[0].date()
    latest_consumption = ec_dates[ec_dates.count() - 1].date()
    days_diff = (latest_consumption - first_consumption).days

    print()

    for counter in range(1, days_diff + 1):
        print(" --- Generating day statistics for day {} of {}".format(counter, days_diff))
        # Just call analyze for each day. If we missed a day or so, the backend will regenerate it.
        dsmr_stats.services.analyze()


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0014_settings_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='DayStatistics',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('hour_start', models.DateTimeField(unique=True)),
                ('electricity1', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity2', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity1_returned', models.DecimalField(decimal_places=3, max_digits=9)),
                ('electricity2_returned', models.DecimalField(decimal_places=3, max_digits=9)),
                ('gas', models.DecimalField(default=None, decimal_places=3, null=True, max_digits=9)),
            ],
        ),
        migrations.RunPython(recalculate_statistics),
    ]
