# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils.translation import ugettext_lazy as _


def insert_notifications(apps, schema_editor):
    import dsmr_frontend.services
    Notification = apps.get_model('dsmr_frontend', 'Notification')

    Notification.objects.create(
        message=dsmr_frontend.services.get_translated_string(
            text=_(
                "It's now possible to automatically export your gas meter positions to your own Mindergas.nl account! "
                "See the FAQ in the documentation for a guide on how to create and/or link your account."
            )
        ),
        redirect_to='frontend:docs-redirect'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_frontend', '0005_notifications'),
        ('dsmr_mindergas', '0001_mindergas'),
    ]

    operations = [
        migrations.RunPython(insert_notifications),
    ]
