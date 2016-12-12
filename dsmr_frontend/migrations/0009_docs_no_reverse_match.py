# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def convert_notifications(apps, schema_editor):
    """ Fixes any broken URL's in pending migrations due to: NoReverseMatch at / Reverse for 'docs' #175. """
    Notification = apps.get_model('dsmr_frontend', 'Notification')
    Notification.objects.filter(redirect_to='frontend:docs').update(redirect_to='frontend:docs-redirect')


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_frontend', '0008_merge_electricity_tariffs_notification'),
    ]

    operations = [
        migrations.RunPython(convert_notifications),
    ]
