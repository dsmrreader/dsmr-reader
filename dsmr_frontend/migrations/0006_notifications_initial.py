# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils import timezone
from django.db import migrations
from django.db.migrations.recorder import MigrationRecorder
from django.utils.translation import ugettext_lazy as _


def insert_notifications(apps, schema_editor):
    import dsmr_frontend.services
    Notification = apps.get_model('dsmr_frontend', 'Notification')

    # Search for any applied migrations in the past. This should indicate a long(er) living instance of the project.
    existing_project = MigrationRecorder.Migration.objects.filter(
        applied__lt=timezone.now() - timezone.timedelta(hours=24)
    ).exists()

    if existing_project:
        return

    Notification.objects.create(
        message=dsmr_frontend.services.get_translated_string(
            text=_('Welcome to DSMR-reader! Please make sure to check your settings in the Configuration page!')
        ),
        redirect_to='admin:index'
    )

    Notification.objects.create(
        message=dsmr_frontend.services.get_translated_string(
            text=_('You may check the status of your readings and data in the Status page.')
        ),
        redirect_to='frontend:status'
    )


class Migration(migrations.Migration):
    dependencies = [
        ('dsmr_frontend', '0005_notifications'),
    ]

    operations = [
        migrations.RunPython(insert_notifications),
    ]
