# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0012_meta'),
    ]

    operations = [
        # The model will be recreated, but this makes sure the data is dropped first as well.
        migrations.DeleteModel(
            name='ElectricityStatistics',
        ),
    ]
