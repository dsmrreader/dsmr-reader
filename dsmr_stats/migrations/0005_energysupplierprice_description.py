# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0004_energysupplierprice_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='energysupplierprice',
            name='description',
            field=models.CharField(help_text='For your own reference, i.e. your supplier name', max_length=255, null=True, blank=True),
        ),
    ]
