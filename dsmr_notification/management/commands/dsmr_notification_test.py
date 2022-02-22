from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

import dsmr_notification.services
from dsmr_stats.models.statistics import DayStatistics


class Command(BaseCommand):
    help = _('Sends a test notification to your device (if any).')

    def handle(self, **options):
        try:
            day_statistics = DayStatistics.objects.all().order_by('-day')[0]
        except IndexError:
            message = 'Test. 1. 2. 3.'
        else:
            message = dsmr_notification.services.create_consumption_message(day_statistics)

        dsmr_notification.services.send_notification(title='Test message from DSMR-reader', message=message)
