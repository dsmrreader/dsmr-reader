# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys

from django.db import migrations


def check_renamed_migrations(*args, **kwargs):
    RENAMED_MIGRATIONS = {
        '0002_auto_20151113_1936': '0002_consumption_models',
        '0003_auto_20151113_2012': '0003_consumption_date_fields',
        '0004_auto_20151118_2120': '0004_energysupplierprice_models',
    }

    migrations_to_rename = migrations.recorder.MigrationRecorder.Migration.objects.filter(
        app='dsmr_stats', name__in=RENAMED_MIGRATIONS.keys()
    )
    print (migrations_to_rename, bool(migrations_to_rename))

    for current_migration in migrations_to_rename:
        print(current_migration.pk)
        current_migration.name = RENAMED_MIGRATIONS[current_migration.name]
        current_migration.save(update_fields=['name'])

    if migrations_to_rename:
        print (
            'We found legacy migrations which were renamed later on. We fixed it in the database, '
            'but were unable to stop duplicate migrations. Please re-apply migrations again as '
            'these migrations will be marked completed this time and this message remains hidden :]',
            file=sys.stderr
        )


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_stats', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(check_renamed_migrations),
    ]
