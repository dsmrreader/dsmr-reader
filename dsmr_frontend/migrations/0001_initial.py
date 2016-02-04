# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FrontendSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('reverse_dashboard_graphs', models.BooleanField(verbose_name='Reverse dashboard graphs', default=False, help_text='Whether graphs are rendered with an reversed X-axis')),
            ],
            options={
                'verbose_name': 'Frontend configuration',
                'default_permissions': (),
            },
        ),
    ]
