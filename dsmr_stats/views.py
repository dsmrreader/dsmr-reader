import json

from django.conf import settings
from django.utils import timezone
from django.views.generic.base import TemplateView, View
from chartjs.views.lines import BaseLineChartView

from dsmr_stats.models import DsmrReading, ElectricityConsumption, GasConsumption, \
    ElectricityStatistics, EnergySupplierPrice
import dsmr_stats.services
from _collections import defaultdict
from django.http.response import HttpResponse


class Dashboard(TemplateView):
    template_name = 'dsmr_stats/dashboard.html'

    def get_context_data(self, **kwargs):
        context_data = super(Dashboard, self).get_context_data(**kwargs)

        try:
            context_data['consumption'] = dsmr_stats.services.day_consumption(
                day=timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
            )
        except LookupError:
            pass

        return context_data


class History(TemplateView):
    template_name = 'dsmr_stats/history.html'

    def get_context_data(self, **kwargs):
        context_data = super(History, self).get_context_data(**kwargs)
        context_data['usage'] = []

        # @TODO: There must be a way to make this cleaner.
        context_data['chart'] = defaultdict(list)

        # Summarize stats for the past two weeks.
        now = timezone.now().astimezone(settings.LOCAL_TIME_ZONE)

        for current_day in (now - timezone.timedelta(days=n) for n in range(1, 15)):
            current_day = current_day.astimezone(settings.LOCAL_TIME_ZONE)

            try:
                day_consumption = dsmr_stats.services.day_consumption(day=current_day)
            except LookupError:
                continue

            context_data['usage'].append(day_consumption)
            context_data['chart']['days'].append(current_day.strftime("%a %d-%m"))
            context_data['chart']['electricity1_cost'].append(float(
                day_consumption['electricity1_cost']
            ))
            context_data['chart']['electricity2_cost'].append(float(
                day_consumption['electricity2_cost']
            ))
            context_data['chart']['gas_cost'].append(float(day_consumption['gas_cost']))
            context_data['chart']['total_cost'].append(float(day_consumption['total_cost']))

        for key, value in context_data['chart'].items():
            context_data['chart'][key] = json.dumps(value)

        return context_data


class Statistics(TemplateView):
    template_name = 'dsmr_stats/statistics.html'

    def get_context_data(self, **kwargs):
        context_data = super(Statistics, self).get_context_data(**kwargs)
        context_data['dsmr_stats'] = ElectricityStatistics.objects.all().order_by('-pk')[0]
        context_data['total_readings'] = DsmrReading.objects.count()
        context_data['first_reading'] = DsmrReading.objects.all().order_by('pk')[0].timestamp
        context_data['last_reading'] = DsmrReading.objects.all().order_by('-pk')[0].timestamp
        context_data['consumption'] = dsmr_stats.services.day_consumption(
            day=timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
        )
        return context_data


class EnergySupplierPrices(TemplateView):
    template_name = 'dsmr_stats/energy_supplier_prices.html'

    def get_context_data(self, **kwargs):
        context_data = super(EnergySupplierPrices, self).get_context_data(**kwargs)
        context_data['prices'] = EnergySupplierPrice.objects.all()
        return context_data


class ChartDataMixin(BaseLineChartView):
    consumption_model = None
    reading_count = 72

    def _get_readings(self, **kwargs):
        return self.consumption_model.objects.all().order_by('-id')[:self.reading_count]

    def normalize(self, value):
        return value

    def get_labels(self):
        y_axis = []

        # Make sure we use local time zone.
        for read_at in self._get_readings().values_list('read_at', flat=True):
            y_axis.append(
                read_at.astimezone(settings.LOCAL_TIME_ZONE).strftime("%H:%M:%S")
            )

        return y_axis

    def get_data(self):
        readings = []
        data = self._get_readings().values_list('currently_delivered', flat=True)

        for currently_delivered in data:
            readings.append(self.normalize(currently_delivered))

        return [readings]


class RecentElectricityData(ChartDataMixin):
    consumption_model = ElectricityConsumption
    reading_count = 48

    def normalize(self, value):
        return value * 1000


class RecentGasData(ChartDataMixin):
    consumption_model = GasConsumption


class LatestData(View):
    def get(self, request):
        ec = ElectricityConsumption.objects.all().order_by('-pk')[0].currently_delivered
        gc = GasConsumption.objects.all().order_by('-pk')[0].currently_delivered
        return HttpResponse(json.dumps({
            'electricity': float(ec * 1000), 'gas': float(gc),
        }), content_type='application/json')
