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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('daily_backup', models.BooleanField(verbose_name='Backup daily', default=True, help_text='Create a backup of your data daily. Stored locally, but can be exported using Dropbox.')),
                ('compress', models.BooleanField(verbose_name='Compress', default=True, help_text='Create backups in compressed (gzip) format, saving a significant amount of disk space.')),
                ('backup_time', models.TimeField(verbose_name='Backup timestamp', default=datetime.time(2, 0), help_text='Daily moment of creating the backup. You should prefer a nightly timestamp, as it might freeze or lock the application shortly during backup creation.')),
                ('latest_backup', models.DateTimeField(null=True, verbose_name='Latest backup', blank=True, default=None, help_text='Timestamp of latest backup created. Automatically updated by application. Please note that the application will ignore the "backup_time" setting the first time used.')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Backup configuration',
            },
        ),
        migrations.CreateModel(
            name='DropboxSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('access_token', models.CharField(null=True, verbose_name='Dropbox access token', help_text='The access token for your Dropbox account. You should register an App for your own Dropbox account (https://www.dropbox.com/developers/apps). Please select "Permission type" named "App folder" to restrict unneeded access. Backups will be synced to a dedicated folder in your account. After creating your App you should be able to generate an "Access token" and enter it here. See https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/ for more information.', blank=True, max_length=128, default=None)),
                ('latest_sync', models.DateTimeField(null=True, verbose_name='Latest sync', blank=True, default=None, help_text='Timestamp of latest sync with Dropbox. Automatically updated by application.')),
            ],
            options={
                'default_permissions': (),
                'verbose_name': 'Dropbox configuration',
            },
        ),
    ]
