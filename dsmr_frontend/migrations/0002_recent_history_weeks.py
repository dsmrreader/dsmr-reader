# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dsmr_frontend", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="frontendsettings",
            name="recent_history_weeks",
            field=models.IntegerField(
                help_text="The number of weeks displayed in the recent history overview.",
                default=4,
                choices=[
                    (1, "Last week"),
                    (2, "Last two weeks"),
                    (3, "Last three weeks"),
                    (4, "Last four weeks"),
                    (5, "Last five weeks"),
                ],
                verbose_name="Recent history weeks",
            ),
        ),
    ]
