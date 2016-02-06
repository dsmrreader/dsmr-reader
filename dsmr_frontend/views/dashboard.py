import json

from django.views.generic.base import TemplateView
from django.conf import settings

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings
import dsmr_consumption.services
import dsmr_stats.services


class Dashboard(TemplateView):
    template_name = 'dsmr_frontend/dashboard.html'
    electricity_max = 30
    gas_max = 36
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
            [x.read_at.astimezone(
                settings.LOCAL_TIME_ZONE
            ).strftime("%a %H:%M") for x in electricity]
        )
        context_data['electricity_y'] = json.dumps(
            [float(x.currently_delivered * 1000) for x in electricity]
        )

        context_data['gas_x'] = json.dumps(
            [x.read_at.astimezone(
                settings.LOCAL_TIME_ZONE
            ).strftime("%a %H:%M") for x in gas]
        )
        context_data['gas_y'] = json.dumps(
            [float(x.currently_delivered) for x in gas]
        )

        context_data['track_temperature'] = WeatherSettings.get_solo().track

        if context_data['track_temperature']:
            context_data['temperature_x'] = json.dumps(
                [x.read_at.astimezone(
                    settings.LOCAL_TIME_ZONE
                ).strftime("%a %H:%M") for x in temperature]
            )
            context_data['temperature_y'] = json.dumps(
                [float(x.degrees_celcius) for x in temperature]
            )

        latest_electricity = ElectricityConsumption.objects.all().order_by('-read_at')[0]
        latest_gas = GasConsumption.objects.all().order_by('-read_at')[0]

        context_data['latest_electricity_read'] = latest_electricity.read_at
        context_data['latest_electricity'] = int(
            latest_electricity.currently_delivered * 1000
        )
        context_data['latest_electricity_returned'] = int(
            latest_electricity.currently_returned * 1000
        )

        context_data['latest_gas_read'] = latest_gas.read_at
        context_data['latest_gas'] = latest_gas.currently_delivered

        # Average of 'currently delivered' in Watt.
        avg_electricity_delivered_per_hour = dsmr_consumption.services.average_electricity_delivered_by_hour()
        context_data['avg_electricity_delivered'] = json.dumps(
            [
                {
                    'value': float(dsmr_consumption.services.round_decimal(x['avg_delivered'] * 1000)),
                    'color': str(self._hour_to_color(x['hour'], 0x3D9970)),
                    'label': '{}:00'.format(int(x['hour'])),
                    'highlight': '#5AD3D1',
                }
                for x in avg_electricity_delivered_per_hour
            ]
        )

        # Average of real usage per hour, in kWh,
        average_consumption_by_hour = dsmr_stats.services.average_consumption_by_hour()
        context_data['avg_consumption_x'] = json.dumps(
            ['{}:00'.format(int(x['hour_start'])) for x in average_consumption_by_hour]
        )

        # @TODO: This should be packed into a helper or something.
        context_data['avg_electricity1_consumption'] = json.dumps(
            [
                {
                    'value': float(dsmr_consumption.services.round_decimal(x['avg_electricity1'])),
                    'color': str(self._hour_to_color(x['hour_start'], 0xF05050)),
                    'label': '{}:00'.format(int(x['hour_start'])),
                    'highlight': '#5AD3D1',
                }
                for x in average_consumption_by_hour
            ]
        )

        context_data['avg_electricity2_consumption'] = json.dumps(
            [
                {
                    'value': float(dsmr_consumption.services.round_decimal(x['avg_electricity2'])),
                    'color': self._hour_to_color(x['hour_start'], 0xF05050),
                    'label': '{}:00'.format(int(x['hour_start'])),
                    'highlight': '#5AD3D1',
                }
                for x in average_consumption_by_hour
            ]
        )

        context_data['avg_gas_consumption'] = json.dumps(
            [
                {
                    'value': float(dsmr_consumption.services.round_decimal(x['avg_gas'])),
                    'color': self._hour_to_color(x['hour_start'], 0xFF851B),
                    'label': '{}:00'.format(int(x['hour_start'])),
                    'highlight': '#5AD3D1',
                }
                for x in average_consumption_by_hour
            ]
        )

        try:
            context_data['consumption'] = dsmr_consumption.services.day_consumption(
                day=latest_electricity.read_at.astimezone(settings.LOCAL_TIME_ZONE).date()
            )
        except LookupError:
            pass

        return context_data

    def _hour_to_color(self, hour, offset=0):
        """ A little help to render 'random' colors, making the graphs look less dull. """
        # Offset 4000000 = purple.
        return '#%06x' % int(hour * 5 + int(offset))
