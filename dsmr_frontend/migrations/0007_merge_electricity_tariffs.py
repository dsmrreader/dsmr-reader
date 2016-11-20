# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_frontend', '0006_notifications_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='frontendsettings',
            name='merge_electricity_tariffs',
            field=models.BooleanField(default=False, help_text='Whether you are using a single electricity tariff and both (high/low) should be displayed merged', verbose_name='Merge electricity tariffs'),
        ),
    ]
