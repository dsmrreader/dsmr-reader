# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_stats", "0005_statistics_exportverbose_names"),
    ]

    operations = [
        migrations.AddField(
            model_name="daystatistics",
            name="highest_temperature",
            field=models.DecimalField(
                decimal_places=1,
                max_digits=4,
                verbose_name="Highest temperature",
                default=None,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="daystatistics",
            name="lowest_temperature",
            field=models.DecimalField(
                decimal_places=1,
                max_digits=4,
                verbose_name="Lowest temperature",
                default=None,
                null=True,
            ),
        ),
    ]
