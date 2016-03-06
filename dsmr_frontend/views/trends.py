import json

from django.views.generic.base import TemplateView

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
import dsmr_consumption.services
import dsmr_frontend.services
import dsmr_stats.services


class Trends(TemplateView):
    template_name = 'dsmr_frontend/trends.html'

    def get_context_data(self, **kwargs):
        capabilities = dsmr_frontend.services.get_data_capabilities()

        context_data = super(Trends, self).get_context_data(**kwargs)
        context_data['capabilities'] = capabilities

        context_data['day_statistics_count'] = DayStatistics.objects.count()
        context_data['hour_statistics_count'] = HourStatistics.objects.count()

        if not capabilities['any']:
            return context_data

        # Average of power demand in Watt.
        avg_electricity_demand_per_hour = dsmr_consumption.services.average_electricity_demand_by_hour()

        # Average of real consumption/return per hour.
        average_consumption_by_hour = dsmr_stats.services.average_consumption_by_hour()

        context_data['avg_consumption_x'] = json.dumps(
            ['{}:00'.format(int(x['hour_start'])) for x in average_consumption_by_hour]
        )

        if capabilities['electricity']:
            context_data['avg_electricity_delivered'] = self._map_graph_data_to_json(
                avg_electricity_demand_per_hour,
                'hour',
                'avg_delivered',
                '#F05050',
                y_type=int,
                y_multiply=1000
            )

            context_data['avg_electricity1_consumption'] = self._map_graph_data_to_json(
                average_consumption_by_hour,
                'hour_start',
                'avg_electricity1',
                '#F05050'
            )
            context_data['avg_electricity2_consumption'] = self._map_graph_data_to_json(
                average_consumption_by_hour,
                'hour_start',
                'avg_electricity2',
                '#F05050'
            )

        if capabilities['electricity_returned']:
            context_data['avg_electricity_returned'] = self._map_graph_data_to_json(
                avg_electricity_demand_per_hour,
                'hour',
                'avg_returned',
                '#27C24C',
                y_type=int,
                y_multiply=1000
            )

            context_data['avg_electricity1_returned_yield'] = self._map_graph_data_to_json(
                average_consumption_by_hour,
                'hour_start',
                'avg_electricity1_returned',
                '#27C24C'
            )
            context_data['avg_electricity2_returned_yield'] = self._map_graph_data_to_json(
                average_consumption_by_hour,
                'hour_start',
                'avg_electricity2_returned',
                '#27C24C'
            )

        if capabilities['gas']:
            context_data['avg_gas_consumption'] = self._map_graph_data_to_json(
                average_consumption_by_hour,
                'hour_start',
                'avg_gas',
                '#FF851B'
            )

        return context_data

    def _map_graph_data_to_json(self, data, x_field, y_field, color, y_type=float, y_multiply=1):
        """ Helper to iterate all data, extract the fields we need andmapping then to JSON. """
        return json.dumps(
            [
                {
                    'value': y_type(dsmr_consumption.services.round_decimal(i[y_field] * y_multiply)),
                    'color': color,
                    'label': '{}:00'.format(int(i[x_field])),
                    'highlight': '#5AD3D1',
                }
                for i in data
            ]
        )
