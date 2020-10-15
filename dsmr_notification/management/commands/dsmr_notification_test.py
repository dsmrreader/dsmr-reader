from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

import dsmr_notification.services


class Command(BaseCommand):
    help = _('Sends a test notification to your device (if any).')

    def handle(self, **options):
        dsmr_notification.services.send_notification(
            title='Test title',
            message='Test message from DSMR-reader'
        )
