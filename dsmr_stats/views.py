import pytz

from django.conf import settings
from django.utils import timezone
from django.views.generic.base import TemplateView
from chartjs.views.lines import BaseLineChartView

from dsmr_stats.models import ElectricityConsumption, GasConsumption
import dsmr_stats.services


class Dashboard(TemplateView):
    template_name = 'dsmr_stats/dashboard.html'

    def get_context_data(self, **kwargs):
        context_data = super(Dashboard, self).get_context_data(**kwargs)
        context_data['consumption'] = dsmr_stats.services.day_consumption(
            day=timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
        )
        return context_data

#         # Summarize stats for the past week.
#         now = timezone.now()
#
#         for current_day in (now - timezone.timedelta(days=n) for n in range(7)):
#             current_day = current_day.astimezone(settings.LOCAL_TIME_ZONE)
#             context_data['usage'].append(
#                  dsmr_stats.services.day_consumption(day=current_day)
#             )
#
#         return context_data


class Recent(TemplateView):
    template_name = 'dsmr_stats/recent.html'


class ChartDataMixin(BaseLineChartView):
    consumption_model = None

    def _get_readings(self, **kwargs):
        return self.consumption_model.objects.all().order_by('-id')[:48]

    def normalize(self, value):
        return value

    def get_labels(self):
        y_axis = []

        # Make sure we use local time zone.
        for read_at in self._get_readings().values_list('read_at', flat=True):
            y_axis.append(read_at.astimezone(settings.LOCAL_TIME_ZONE).strftime("%H:%M:%S"))

        return y_axis

    def get_data(self):
        readings = []

        for currently_delivered in self._get_readings().values_list('currently_delivered', flat=True):
            readings.append(self.normalize(currently_delivered))

        return [readings]


class PowerData(ChartDataMixin):
    consumption_model = ElectricityConsumption

    def normalize(self, value):
        return value * 1000


class GasData(ChartDataMixin):
    consumption_model = GasConsumption
