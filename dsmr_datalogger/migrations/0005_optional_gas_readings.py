# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_datalogger', '0004_multiple_dsmr_version_support'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dsmrreading',
            name='extra_device_delivered',
            field=models.DecimalField(null=True, default=None, help_text='Last hourly value delivered to client', decimal_places=3, max_digits=9),
        ),
        migrations.AlterField(
            model_name='dsmrreading',
            name='extra_device_timestamp',
            field=models.DateTimeField(null=True, default=None, help_text='Last hourly reading timestamp'),
        ),
    ]
