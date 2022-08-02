# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dsmr_consumption", "0003_electricity_consumption_indexes"),
    ]

    operations = [
        migrations.AlterField(
            model_name="energysupplierprice",
            name="electricity_1_price",
            field=models.DecimalField(
                max_digits=11,
                default=0,
                help_text='Are you using a single tariff? Please enter the same price twice and enable "Merge electricity tariffs" in the frontend configuration',
                decimal_places=5,
                verbose_name="Electricity 1 price (Dutch users: low tariff)",
            ),
        ),
        migrations.AlterField(
            model_name="energysupplierprice",
            name="electricity_2_price",
            field=models.DecimalField(
                max_digits=11,
                default=0,
                help_text='Are you using a single tariff? Please enter the same price twice and enable "Merge electricity tariffs" in the frontend configuration',
                decimal_places=5,
                verbose_name="Electricity 2 price (Dutch users: normal tariff)",
            ),
        ),
    ]
