import pytz

from django.conf import settings
from django.views.generic.base import TemplateView
from chartjs.views.lines import BaseLineChartView

from dsmr_stats.models import ElectricityConsumption, GasConsumption


class Home(TemplateView):
    template_name = 'dsmr_stats/index.html'


class ChartDataMixin(BaseLineChartView):
    consumption_model = None

    def _get_readings(self, **kwargs):
        return self.consumption_model.objects.all().order_by('-id')[:72]

    def get_labels(self):
        y_axis = []
        # Make sure we use local time zone.
        cet_timezone = pytz.timezone(settings.LOCAL_TIME_ZONE)

        for read_at in self._get_readings().values_list('read_at', flat=True):
            y_axis.append(read_at.astimezone(cet_timezone).strftime("%H:%M:%S"))

        return y_axis

    def get_data(self):
        readings = []

        for currently_delivered in self._get_readings().values_list('currently_delivered', flat=True):
            readings.append(currently_delivered)

        return [readings]


class PowerData(ChartDataMixin):
    consumption_model = ElectricityConsumption


class GasData(ChartDataMixin):
    consumption_model = GasConsumption
