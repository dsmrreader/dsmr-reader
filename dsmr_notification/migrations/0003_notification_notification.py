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
                "There is now support for pushing notifications to your phone, summarizing your daily totals! "
                "Both Android and iOS are supported. See the FAQ in the documentation for more information."
            )
        ),
        redirect_to='frontend:docs-redirect'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_frontend', '0005_notifications'),
        ('dsmr_notification', '0002_notificationsetting_next_notification'),
    ]

    operations = [
        migrations.RunPython(insert_notifications),
    ]
