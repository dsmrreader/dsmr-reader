# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("dsmr_frontend", "0002_recent_history_weeks"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="frontendsettings",
            name="recent_history_weeks",
        ),
    ]
