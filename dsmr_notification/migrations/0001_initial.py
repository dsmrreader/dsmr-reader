# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationSetting',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('send_notification', models.BooleanField(help_text='Whether or not you want to receive a notification of your daily usage on your smartphone', verbose_name='Send notification', default=False)),
                ('notification_service', models.CharField(help_text='Which notification service to use for sending daily usage notifications', max_length=20, choices=[('nma', 'NotifyMyAndroid'), ('prowl', 'Prowl')], verbose_name='Notification service', default='nma')),
                ('api_key', models.CharField(help_text='The API key used send messages to your smartphone. Please visit https://notifymyandroid.com/ or https://www.prowlapp.com/ to download and use the apps.', default=None, null=True, verbose_name='Notification service API key', blank=True, max_length=64)),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Notification configuration',
            },
        ),
    ]
