# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_datalogger', '0003_split_dsmr_reading_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataloggersettings',
            name='baud_rate',
        ),
        migrations.AddField(
            model_name='dataloggersettings',
            name='dsmr_version',
            field=models.IntegerField(choices=[(4, 'DSMR version 4'), (3, 'DSMR version 2/3')], help_text='The DSMR version your meter supports. Version should be printed on meter.', default=4, verbose_name='DSMR version'),
        ),
    ]
