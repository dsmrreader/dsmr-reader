import json

from django.contrib.humanize.templatetags.humanize import intcomma
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_backend.services
import dsmr_consumption.services


class Statistics(TemplateView):
    template_name = 'dsmr_frontend/statistics.html'

    def get_context_data(self, **kwargs):
        context_data = super(Statistics, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()

        try:
            latest_reading = DsmrReading.objects.all().order_by('-pk')[0]
        except IndexError:
            pass
        else:
            context_data['latest_reading'] = latest_reading
            context_data['delivered_sum'] = latest_reading.electricity_delivered_1 + \
                latest_reading.electricity_delivered_2
            context_data['returned_sum'] = latest_reading.electricity_returned_1 + \
                latest_reading.electricity_returned_2

        today = timezone.localtime(timezone.now()).date()
        context_data['datalogger_settings'] = DataloggerSettings.get_solo()
        context_data['meter_statistics'] = MeterStatistics.get_solo()

        try:
            context_data['energy_prices'] = EnergySupplierPrice.objects.by_date(today)
        except EnergySupplierPrice.DoesNotExist:
            pass

        return context_data


class StatisticsXhrData(View):
    """ XHR view for fetching the dashboard header, displaying latest readings and price estimate, JSON response. """
    def get(self, request):
        data = {
            'total_reading_count': intcomma(DsmrReading.objects.all().count()),
            'slumber_consumption_watt': dsmr_consumption.services.calculate_slumber_consumption_watt(),
        }

        min_max_consumption_watt = dsmr_consumption.services.calculate_min_max_consumption_watt()
        data.update(min_max_consumption_watt)

        return HttpResponse(json.dumps(data), content_type='application/json')
