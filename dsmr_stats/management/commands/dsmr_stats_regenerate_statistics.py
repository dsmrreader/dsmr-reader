from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_stats.models.statistics import DayStatistics
import dsmr_stats.services


class Command(BaseCommand):
    help = _('Regenerates missing statistics, if any.')

    def handle(self, **options):
        first = ElectricityConsumption.objects.all()[0].read_at
        last = ElectricityConsumption.objects.all().order_by('-read_at')[0].read_at
        days_diff = (last - first).days

        analyzed_days = DayStatistics.objects.all().count()
        days_todo = days_diff - analyzed_days

        for __ in range(1, days_todo + 1):
            # Just call analyze for each day. If we missed a day or so, the backend will regenerate it.
            dsmr_stats.services.analyze()
