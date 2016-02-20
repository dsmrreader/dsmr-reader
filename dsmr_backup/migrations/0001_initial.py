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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('daily_backup', models.BooleanField(verbose_name='Backup daily', help_text='Create a backup of your data daily. Stored locally, but can be exported using Dropbox.', default=True)),
                ('compress', models.BooleanField(verbose_name='Compress', help_text='Create backups in compressed (gzip) format, saving a significant amount of disk space.', default=True)),
                ('backup_time', models.TimeField(verbose_name='Backup timestamp', help_text='Daily moment of creating the backup. You should prefer a nightly timestamp, as it might freeze or lock the application shortly during backup creation.', default=datetime.time(2, 0))),
                ('latest_backup', models.DateTimeField(null=True, help_text='Timestamp of latest backup created. Automatically updated by application. Please note that the application will ignore the "backup_time" setting the first time used.', default=None, blank=True)),
            ],
            options={
                'verbose_name': 'Backup configuration',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='DropboxSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('access_token', models.CharField(verbose_name='Dropbox access token', null=True, max_length=128, help_text='The access token for your Dropbox account. You should register an App for your own Dropbox account (https://www.dropbox.com/developers/apps). Please select "Permission type" named "App folder" to restrict unneeded access. Backups will be synced to a dedicated folder in your account. After creating your App you should be able to generate an "Access token" and enter it here. See https://blogs.dropbox.com/developers/2014/05/generate-an-access-token-for-your-own-account/ for more information.', default=None, blank=True)),
                ('latest_sync', models.DateTimeField(null=True, help_text='Timestamp of latest sync with Dropbox. Automatically updated by application.', default=None, blank=True)),
            ],
            options={
                'verbose_name': 'Dropbox configuration',
                'default_permissions': (),
            },
        ),
    ]
