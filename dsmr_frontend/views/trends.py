import json

from django.views.generic.base import TemplateView

from dsmr_stats.models.settings import StatsSettings
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
import dsmr_consumption.services
import dsmr_stats.services


class Trends(TemplateView):
    template_name = 'dsmr_frontend/trends.html'

    def get_context_data(self, **kwargs):
        context_data = super(Trends, self).get_context_data(**kwargs)
        context_data['stats_settings'] = StatsSettings.get_solo()

        # Average of 'currently delivered' in Watt.
        avg_electricity_delivered_per_hour = dsmr_consumption.services.average_electricity_delivered_by_hour()
        context_data['avg_electricity_delivered'] = json.dumps(
            [
                {
                    'value': int(dsmr_consumption.services.round_decimal(x['avg_delivered'] * 1000)),
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

        # @TODO: This should be packed into a helper or something, since it is used three times.
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
        context_data['day_statistics_count'] = DayStatistics.objects.count()
        context_data['hour_statistics_count'] = HourStatistics.objects.count()

        return context_data

    def _hour_to_color(self, hour, offset=0):
        """ A little help to render 'random' colors, making the graphs look less dull. """
        hour = int(hour)
        offset = int(offset)
        return '#%06x' % int(hour * 5 + offset)
