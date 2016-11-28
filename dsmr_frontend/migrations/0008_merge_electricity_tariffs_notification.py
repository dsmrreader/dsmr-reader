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
                "It's now possible to have the electricity tariffs merged to a single one. This might come handy when "
                "you pay your energy supplier fo a single tariff instead of high/low. You can enable this feature in "
                " frontend configuration: 'Merge electricity tariffs'"
            )
        ),
        redirect_to='admin:index'
    )


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_frontend', '0007_merge_electricity_tariffs'),
    ]

    operations = [
        migrations.RunPython(insert_notifications),
    ]
