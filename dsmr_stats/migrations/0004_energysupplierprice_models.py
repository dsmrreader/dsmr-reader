# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0003_consumption_date_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnergySupplierPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('start', models.DateField()),
                ('end', models.DateField(null=True, blank=True)),
                ('electricity_1_price', models.DecimalField(decimal_places=5, max_digits=11)),
                ('electricity_2_price', models.DecimalField(decimal_places=5, max_digits=11)),
                ('gas_price', models.DecimalField(decimal_places=5, max_digits=11)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='energysupplierprice',
            unique_together=set([('start', 'end')]),
        ),
    ]
