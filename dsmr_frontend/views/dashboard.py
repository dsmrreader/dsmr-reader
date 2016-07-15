import json

from django.views.generic.base import TemplateView
from django.utils import formats, timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_frontend.models.message import Notification
import dsmr_consumption.services
import dsmr_backend.services
import dsmr_stats.services


class Dashboard(TemplateView):
    template_name = 'dsmr_frontend/dashboard.html'
    electricity_max = 30  # Minutes or readings.
    gas_max = 25  # Hours.
    temperature_max = gas_max

    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()
        context_data = super(Dashboard, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['frontend_settings'] = frontend_settings
        context_data['notifications'] = Notification.objects.unread()

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
                timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_TIME_FORMAT'
            ) for x in electricity]
        )
        context_data['electricity_y'] = json.dumps(
            [float(x.currently_delivered * 1000) for x in electricity]
        )
        context_data['electricity_returned_y'] = json.dumps(
            [float(x.currently_returned * 1000) for x in electricity]
        )

        context_data['gas_x'] = json.dumps(
            [formats.date_format(
                timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_TIME_FORMAT'
            ) for x in gas]
        )
        context_data['gas_y'] = json.dumps(
            [float(x.currently_delivered) for x in gas]
        )

        context_data['track_temperature'] = WeatherSettings.get_solo().track
        context_data['temperature_count'] = temperature.count()

        if context_data['track_temperature']:
            context_data['temperature_x'] = json.dumps(
                [formats.date_format(
                    timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_TIME_FORMAT'
                ) for x in temperature]
            )
            context_data['temperature_y'] = json.dumps(
                [float(x.degrees_celcius) for x in temperature]
            )

            try:
                latest_temperature = TemperatureReading.objects.all().order_by('-read_at')[0]
            except IndexError:
                pass
            else:
                context_data['latest_temperature_read'] = latest_temperature.read_at
                context_data['latest_temperature'] = latest_temperature.degrees_celcius

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
            pass
        else:
            context_data['latest_gas_read'] = latest_gas.read_at
            context_data['latest_gas'] = latest_gas.currently_delivered

        context_data['consumption'] = dsmr_consumption.services.day_consumption(
            day=timezone.localtime(latest_electricity.read_at).date()
        )
        today = timezone.localtime(timezone.now()).date()
        context_data['month_statistics'] = dsmr_stats.services.month_statistics(target_date=today)
        return context_data
