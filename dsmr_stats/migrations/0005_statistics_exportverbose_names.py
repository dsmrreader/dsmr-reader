# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dsmr_stats", "0004_hour_statistics_gas_default_retroactive"),
    ]

    operations = [
        migrations.AlterField(
            model_name="daystatistics",
            name="average_temperature",
            field=models.DecimalField(
                decimal_places=1,
                verbose_name="Average temperature",
                null=True,
                default=None,
                max_digits=4,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="day",
            field=models.DateField(unique=True, verbose_name="Date"),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="electricity1",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Electricity 1 (Dutch users: low tariff)",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="electricity1_cost",
            field=models.DecimalField(
                decimal_places=2,
                verbose_name="Electricity 1 price (Dutch users: low tariff)",
                max_digits=8,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="electricity1_returned",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Electricity 1 returned (Dutch users: low tariff)",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="electricity2",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Electricity 2 (Dutch users: normal tariff)",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="electricity2_cost",
            field=models.DecimalField(
                decimal_places=2,
                verbose_name="Electricity 2 price (Dutch users: normal tariff)",
                max_digits=8,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="electricity2_returned",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Electricity 2 returned (Dutch users: normal tariff)",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="gas",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Gas",
                null=True,
                default=None,
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="gas_cost",
            field=models.DecimalField(
                decimal_places=2,
                verbose_name="Gas cost",
                null=True,
                default=None,
                max_digits=8,
            ),
        ),
        migrations.AlterField(
            model_name="daystatistics",
            name="total_cost",
            field=models.DecimalField(
                decimal_places=2, verbose_name="Total cost", max_digits=8
            ),
        ),
        migrations.AlterField(
            model_name="hourstatistics",
            name="electricity1",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Electricity 1 (Dutch users: low tariff)",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="hourstatistics",
            name="electricity1_returned",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Electricity 1 returned (Dutch users: low tariff)",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="hourstatistics",
            name="electricity2",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Electricity 2 (Dutch users: normal tariff)",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="hourstatistics",
            name="electricity2_returned",
            field=models.DecimalField(
                decimal_places=3,
                verbose_name="Electricity 2 returned (Dutch users: normal tariff)",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="hourstatistics",
            name="gas",
            field=models.DecimalField(
                decimal_places=3, verbose_name="Gas", max_digits=9, default=0
            ),
        ),
        migrations.AlterField(
            model_name="hourstatistics",
            name="hour_start",
            field=models.DateTimeField(unique=True, verbose_name="Hour start"),
        ),
    ]
