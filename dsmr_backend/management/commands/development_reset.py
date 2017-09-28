from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.conf import settings

from dsmr_backup.models.settings import BackupSettings, DropboxSettings
from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_notification.models.settings import NotificationSetting
from dsmr_api.models import APISettings
from dsmr_frontend.models.message import Notification


class Command(BaseCommand):
    help = _('Resets the environment for development purposes. Not intended for production.')

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--no-api',
            action='store_true',
            dest='no_api',
            default=False,
            help=_('Whether the API should be disabled.')
        )

    def handle(self, **options):
        if not settings.DEBUG:
            raise CommandError(_('Intended usage is NOT production! Only allowed when DEBUG = True'))

        # Just wipe all settings which can affect the environment.
        APISettings.objects.update(allow=not options['no_api'], auth_key='test')
        BackupSettings.objects.update(daily_backup=False)
        DropboxSettings.objects.update(access_token=None)
        MinderGasSettings.objects.update(export=False, auth_token=None)
        NotificationSetting.objects.update(send_notification=False, api_key=None)
        Notification.objects.update(read=True)

        try:
            # Reset passwd.
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            User.objects.create_superuser('admin', 'root@localhost', 'admin')
        else:
            admin.set_password('admin')
            admin.save()
