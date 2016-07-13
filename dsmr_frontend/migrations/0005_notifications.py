# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_frontend', '0004_chart_colors'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('message', models.TextField()),
                ('redirect_to', models.CharField(max_length=64, blank=True, default=None, null=True)),
                ('read', models.BooleanField(default=False)),
            ],
            options={
                'default_permissions': (),
            },
        ),
    ]
