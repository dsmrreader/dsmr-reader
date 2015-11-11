from django.views.generic.base import TemplateView
from chartjs.views.lines import BaseLineChartView

from dsmr_stats.models import DsmrReading


class Home(TemplateView):
    template_name = 'dsmr_stats/index.html'


class ChartDataMixin(BaseLineChartView):
    def _get_readings(self, **kwargs):
        return DsmrReading.objects.all().order_by('-id')[:60]

    def get_labels(self):
        y_axis = []

        for timestamp in self._get_readings().values_list('timestamp', flat=True):
            y_axis.append(timestamp.strftime("%H:%M:%S"))
            
        return y_axis

    def get_combined_data(self):
        power_readings = []
        gas_readings = []
        
        for power in self._get_readings().values_list('electricity_currently_delivered', flat=True):
            power_readings.append(int(power * 1000))        

        for gas in self._get_readings().values_list('extra_device_delivered', flat=True):
            gas_readings.append(int(gas))

        return power_readings, gas_readings
   

class PowerData(ChartDataMixin):
    def get_data(self):
        power, _ = self.get_combined_data()
        return [power]

    
class GasData(ChartDataMixin):
    def get_data(self):
        _, gas = self.get_combined_data()
        return [gas]
