# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def insert_notifications(apps, schema_editor):
    # Removed for new installations.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("dsmr_frontend", "0005_notifications"),
        ("dsmr_notification", "0002_notificationsetting_next_notification"),
    ]

    operations = [
        migrations.RunPython(insert_notifications),
    ]
