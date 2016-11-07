# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_notification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationsetting',
            name='next_notification',
            field=models.DateField(null=True, blank=True, verbose_name='Next notification', default=None, help_text='Timestamp of the next notification. Managed by application.'),
        ),
    ]
