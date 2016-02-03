# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0011_delete_moved_models'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='electricitystatistics',
            options={'default_permissions': ()},
        ),
        migrations.AlterModelOptions(
            name='note',
            options={'verbose_name_plural': 'Notes', 'verbose_name': 'Note', 'default_permissions': ()},
        ),
        migrations.AlterField(
            model_name='note',
            name='day',
            field=models.DateField(verbose_name='Day'),
        ),
        migrations.AlterField(
            model_name='note',
            name='description',
            field=models.CharField(verbose_name='Description', max_length=256),
        ),
    ]
