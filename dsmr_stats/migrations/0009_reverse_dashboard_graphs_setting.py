# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0008_statssettings_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='statssettings',
            name='reverse_dashboard_graphs',
            field=models.BooleanField(verbose_name='Reverse dashboard graphs', default=False, help_text='Whether graphs are rendered with an reversed X-axis.'),
        ),
    ]
