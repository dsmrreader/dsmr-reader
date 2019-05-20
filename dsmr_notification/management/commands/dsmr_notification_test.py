from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

import dsmr_notification.services


class Command(BaseCommand):
    help = _('Sends a test notification to your device (if any).')

    def handle(self, **options):
        dsmr_notification.services.send_notification(
            message='Test message from DSMR-reader', title='Test title'
        )
