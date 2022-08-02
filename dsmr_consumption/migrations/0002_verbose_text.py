# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dsmr_consumption", "0001_squashed_0004_recalculate_gas_consumption"),
    ]

    operations = [
        migrations.AlterField(
            model_name="energysupplierprice",
            name="electricity_1_price",
            field=models.DecimalField(
                verbose_name="Electricity 1 price (Dutch users: low tariff)",
                default=0,
                max_digits=11,
                decimal_places=5,
            ),
        ),
        migrations.AlterField(
            model_name="energysupplierprice",
            name="electricity_2_price",
            field=models.DecimalField(
                verbose_name="Electricity 2 price (Dutch users: normal tariff)",
                default=0,
                max_digits=11,
                decimal_places=5,
            ),
        ),
    ]
