import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin


class Command(InterceptCommandStdoutMixin, BaseCommand):
    help = 'DEV ONLY: Dumps the latest migration of each app for locking in a shell script.'

    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError('DEVELOPMENT ONLY')

        current_app = None
        latest_line = None
        lock_content = "#!/usr/bin/env bash\n\n"
        lock_content += "# Dump for DSMR-reader v{}\n".format(settings.DSMRREADER_VERSION)

        for line in self._intercept_command_stdout('showmigrations', no_color=True).split("\n"):
            if line.startswith(' [ ]'):
                raise AssertionError('Unapplied migration found:{}'.format(line))

            if not line.startswith(' [X]'):
                if current_app:
                    lock_content += "./manage.py migrate {} {}\n".format(
                        current_app,
                        latest_line.replace(' [X] ', '')
                    )
                    current_app = None

                if line.startswith('dsmr_'):
                    current_app = line

            latest_line = line

        file_path = os.path.abspath(os.path.join(
            settings.BASE_DIR, 'provisioning/downgrade', 'v{}.sh'.format(settings.DSMRREADER_VERSION)
        ))
        with open(file_path, 'w') as handle:
            handle.write(lock_content)

        print('Locked into', file_path)
