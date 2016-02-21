# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BackupSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('daily_backup', models.BooleanField(default=True, help_text='Create a backup of your data daily. Stored locally, but can be exported using Dropbox.', verbose_name='Backup daily')),
                ('compress', models.BooleanField(default=True, help_text='Create backups in compressed (gzip) format, saving a significant amount of disk space.', verbose_name='Compress')),
                ('backup_time', models.TimeField(default=datetime.time(2, 0), help_text='Daily moment of creating the backup. You should prefer a nightly timestamp, as it might freeze or lock the application shortly during backup creation.', verbose_name='Backup timestamp')),
                ('latest_backup', models.DateTimeField(null=True, default=None, blank=True, help_text='Timestamp of latest backup created. Automatically updated by application. Please note that the application will ignore the "backup_time" setting the first time used.', verbose_name='Latest backup')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Backup configuration',
            },
        ),
        migrations.CreateModel(
            name='DropboxSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('access_token', models.CharField(null=True, default=None, blank=True, verbose_name='Dropbox access token', max_length=128, help_text='The access token for your Dropbox account. You should register an App for your own Dropbox account (https://www.dropbox.com/developers/apps). Please select "Permission type" named "App folder" to restrict unneeded access. Backups will be synced to a dedicated folder in your account. After creating your App you should be able to generate an "Access token" and enter it here. For more information, see https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account')),
                ('latest_sync', models.DateTimeField(null=True, default=None, blank=True, help_text='Timestamp of latest sync with Dropbox. Automatically updated by application.', verbose_name='Latest sync')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Dropbox configuration',
            },
        ),
    ]
