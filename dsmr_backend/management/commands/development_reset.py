from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.conf import settings

from dsmr_backend.models.settings import EmailSettings, BackendSettings
from dsmr_backup.models.settings import BackupSettings, DropboxSettings, EmailBackupSettings
from dsmr_notification.models.settings import NotificationSetting
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_mqtt.models.settings.broker import MQTTBrokerSettings
from dsmr_pvoutput.models.settings import PVOutputAPISettings
from dsmr_mindergas.models.settings import MinderGasSettings
from dsmr_frontend.models.message import Notification
from dsmr_api.models import APISettings
from dsmr_mqtt.models import queue


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
        BackendSettings.objects.update(disable_electricity_returned_capability=False, process_sleep=0)
        BackupSettings.objects.update(daily_backup=False)
        BackupSettings.get_solo().save()  # Trigger signal
        EmailBackupSettings.objects.update(interval=EmailBackupSettings.INTERVAL_NONE)
        EmailBackupSettings.get_solo().save()  # Trigger signal
        EmailSettings.objects.update(
            email_from=None, email_to=None, host=None, port=None, username=None, password=None
        )
        DropboxSettings.objects.update(access_token=None)
        ConsumptionSettings.objects.update(
            electricity_grouping_type=ConsumptionSettings.ELECTRICITY_GROUPING_BY_READING
        )
        MinderGasSettings.objects.update(export=False, auth_token=None)
        NotificationSetting.objects.update(
            notification_service=None, pushover_api_key=None, pushover_user_key=None, prowl_api_key=None
        )
        MQTTBrokerSettings.objects.update(
            hostname='localhost', port=1883, secure=MQTTBrokerSettings.INSECURE, username=None, password=None
        )
        PVOutputAPISettings.objects.update(auth_token=None, system_identifier=None)
        queue.Message.objects.all().delete()
        Notification.objects.update(read=True)
        Notification.objects.create(message='Development reset completed.')

        try:
            admin = User.objects.get(username='admin')
        except User.DoesNotExist:
            User.objects.create_superuser('admin', 'root@localhost', 'admin')
        else:
            admin.set_password('admin')
            admin.save()
