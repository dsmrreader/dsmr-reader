# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0013_drop_old_statistics_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='StatsSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('track', models.BooleanField(default=True, verbose_name='Track trends', help_text='Whether we should track trends by storing daily consumption summaries.')),
            ],
            options={
                'verbose_name': 'Trends & statistics configuration',
                'default_permissions': (),
            },
        ),
    ]
