# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0005_energysupplierprice_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='energysupplierprice',
            name='electricity_1_price',
            field=models.DecimalField(default=0, decimal_places=5, max_digits=11),
        ),
        migrations.AlterField(
            model_name='energysupplierprice',
            name='electricity_2_price',
            field=models.DecimalField(default=0, decimal_places=5, max_digits=11),
        ),
        migrations.AlterField(
            model_name='energysupplierprice',
            name='gas_price',
            field=models.DecimalField(default=0, decimal_places=5, max_digits=11),
        ),
    ]
