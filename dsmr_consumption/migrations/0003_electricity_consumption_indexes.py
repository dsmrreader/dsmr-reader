# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_consumption', '0002_verbose_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='electricityconsumption',
            name='currently_delivered',
            field=models.DecimalField(decimal_places=3, help_text='Actual electricity power delivered (+P) in 1 Watt resolution', db_index=True, max_digits=9),
        ),
        migrations.AlterField(
            model_name='electricityconsumption',
            name='currently_returned',
            field=models.DecimalField(decimal_places=3, help_text='Actual electricity power received (-P) in 1 Watt resolution', db_index=True, max_digits=9),
        ),
    ]
