# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import random
import string

from django.db import migrations


def generate_random_auth_key(apps, schema_editor):
    APISettings = apps.get_model('dsmr_api', 'APISettings')

    if APISettings.objects.exists():
        return

    random_auth_key = ''.join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64)
    )
    APISettings.objects.create(auth_key=random_auth_key)


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_api', '0001_api_settings'),
    ]

    operations = [
        migrations.RunPython(generate_random_auth_key),
    ]
