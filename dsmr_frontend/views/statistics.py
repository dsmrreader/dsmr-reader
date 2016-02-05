import json

from django.views.generic.base import TemplateView
from django.conf import settings
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
import dsmr_consumption.services


class Statistics(TemplateView):
    template_name = 'dsmr_frontend/statistics.html'

    def get_context_data(self, **kwargs):
        context_data = super(Statistics, self).get_context_data(**kwargs)
        today = timezone.now().astimezone(settings.LOCAL_TIME_ZONE).date()
        context_data['latest_reading'] = DsmrReading.objects.all().order_by('-pk')[0]
        context_data['first_reading'] = DsmrReading.objects.all().order_by('pk')[0]
        context_data['total_reading_count'] = DsmrReading.objects.count()

        avg_electricity_per_hour = dsmr_consumption.services.average_electricity_by_hour()
        context_data['avg_electricity_x'] = json.dumps(
            ['{}:00'.format(x['hour']) for x in avg_electricity_per_hour]
        )
        context_data['avg_electricity_y'] = json.dumps(
            [float(x['avg_delivered'] * 1000) for x in avg_electricity_per_hour]
        )
        context_data['average_electricity_by_hour'] = avg_electricity_per_hour

        try:
            context_data['energy_prices'] = EnergySupplierPrice.objects.by_date(today)
        except EnergySupplierPrice.DoesNotExist:
            pass

        return context_data
