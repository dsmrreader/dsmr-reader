# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from dsmr_stats.models.settings import StatsSettings


def initial_data(* args, **kwargs):
    # This persists the model in the database.
    StatsSettings.get_solo()


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0007_daily_user_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatsSettings',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('compactor_grouping_type', models.IntegerField(default=2, choices=[(1, 'By reading (every 10 seconds)'), (2, 'By minute')], help_text='Electricity readings are read every 10 seconds. We can group those for you.', verbose_name='Compactor grouping type')),
            ],
            options={
                'verbose_name': 'Stats configuration',
            },
        ),
        migrations.RunPython(initial_data),
    ]
