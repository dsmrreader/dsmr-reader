import json

from django.views.generic.base import TemplateView
from django.db.models.aggregates import Sum
from django.utils import formats, timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.statistics import DayStatistics
import dsmr_consumption.services


class Dashboard(TemplateView):
    template_name = 'dsmr_frontend/dashboard.html'
    electricity_max = 30  # Minutes or readings.
    gas_max = 24  # Hours.
    temperature_max = gas_max

    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()
        context_data = super(Dashboard, self).get_context_data(**kwargs)

        electricity = ElectricityConsumption.objects.all().order_by('read_at')
        gas = GasConsumption.objects.all().order_by('read_at')
        temperature = TemperatureReading.objects.all().order_by('read_at')

        # User might want to sort things backwards.
        if frontend_settings.reverse_dashboard_graphs:
            electricity = electricity.reverse()[:self.electricity_max]
            gas = gas.reverse()[:self.gas_max]
            temperature = temperature.reverse()[:self.temperature_max]
        else:
            # We can't slice using negative offsets, so we should fetch a (quick) count first)
            electricity_offset = max(0, electricity.count() - self.electricity_max)
            gas_offset = max(0, gas.count() - self.gas_max)
            temperature_offset = max(0, temperature.count() - self.temperature_max)

            electricity = electricity[electricity_offset:]
            gas = gas[gas_offset:]
            temperature = temperature[temperature_offset:]

        context_data['electricity_x'] = json.dumps(
            [formats.date_format(
                timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_DATETIME_FORMAT'
            ) for x in electricity]
        )
        context_data['electricity_y'] = json.dumps(
            [float(x.currently_delivered * 1000) for x in electricity]
        )

        context_data['gas_x'] = json.dumps(
            [formats.date_format(
                timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_DATETIME_FORMAT'
            ) for x in gas]
        )
        context_data['gas_y'] = json.dumps(
            [float(x.currently_delivered) for x in gas]
        )

        context_data['track_temperature'] = WeatherSettings.get_solo().track

        if context_data['track_temperature']:
            context_data['temperature_x'] = json.dumps(
                [formats.date_format(
                    timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_DATETIME_FORMAT'
                ) for x in temperature]
            )
            context_data['temperature_y'] = json.dumps(
                [float(x.degrees_celcius) for x in temperature]
            )

        try:
            latest_electricity = ElectricityConsumption.objects.all().order_by('-read_at')[0]
        except IndexError:
            # Don't even bother when no data available.
            return context_data

        context_data['latest_electricity_read'] = latest_electricity.read_at
        context_data['latest_electricity'] = int(
            latest_electricity.currently_delivered * 1000
        )
        context_data['latest_electricity_returned'] = int(
            latest_electricity.currently_returned * 1000
        )

        try:
            latest_gas = GasConsumption.objects.all().order_by('-read_at')[0]
        except IndexError:
            latest_gas = None
        else:
            context_data['latest_gas_read'] = latest_gas.read_at
            context_data['latest_gas'] = latest_gas.currently_delivered

        context_data['consumption'] = dsmr_consumption.services.day_consumption(
            day=timezone.localtime(latest_electricity.read_at).date()
        )
        now = timezone.localtime(timezone.now()).date()
        start_of_month = timezone.datetime(year=now.year, month=now.month, day=1)
        context_data['month_total'] = DayStatistics.objects.filter(
            day__gte=start_of_month
        ).aggregate(
            total_electricity1=Sum('electricity1'),
            total_electricity1_cost=Sum('electricity1_cost'),
            total_electricity2=Sum('electricity2'),
            total_electricity2_cost=Sum('electricity2_cost'),
            total_electricity1_returned=Sum('electricity1_returned'),
            total_electricity2_returned=Sum('electricity2_returned'),
            total_gas=Sum('gas'),
            total_gas_cost=Sum('gas_cost'),
        )
        return context_data
