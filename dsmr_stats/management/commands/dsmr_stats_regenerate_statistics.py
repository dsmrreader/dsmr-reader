from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_stats.models.statistics import DayStatistics
import dsmr_stats.services


class Command(BaseCommand):
    help = _('Regenerates missing statistics, if any.')

    def handle(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        first_day = DsmrReading.objects.all()[0].timestamp
        days_diff = (timezone.now() - first_day).days

        analyzed_days = DayStatistics.objects.all().count()
        days_todo = days_diff - analyzed_days

        for __ in range(1, days_todo + 1):
            # Just call analyze for each day. If we missed a day or so, the backend will regenerate it.
            dsmr_stats.services.analyze()
