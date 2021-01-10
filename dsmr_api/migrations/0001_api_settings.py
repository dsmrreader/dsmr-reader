# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APISettings',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('allow', models.BooleanField(default=False, help_text='When disabled it will reject incoming requests and return an HTTP 403 error', verbose_name='Enable DSMR-reader API')),
                ('auth_key', models.CharField(verbose_name='Auth Key', default=None, max_length=256, help_text='The auth key used to authenticate for this API.', null=True)),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'API configuration',
            },
        ),
    ]
