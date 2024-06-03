# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_stats", "0002_regenerate_missing_gas_data"),
    ]

    operations = [
        migrations.AlterField(
            model_name="hourstatistics",
            name="gas",
            field=models.DecimalField(max_digits=9, decimal_places=3, default=0),
        ),
    ]
