from collections import defaultdict
import json

from django.views.generic.base import TemplateView
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_frontend.models.settings import FrontendSettings
import dsmr_consumption.services
import dsmr_backend.services
import dsmr_stats.services


class Trends(TemplateView):
    template_name = 'dsmr_frontend/trends.html'

    def get_context_data(self, **kwargs):
        capabilities = dsmr_backend.services.get_capabilities()

        context_data = super(Trends, self).get_context_data(**kwargs)
        context_data['capabilities'] = capabilities
        context_data['frontend_settings'] = FrontendSettings.get_solo()

        context_data['day_statistics_count'] = DayStatistics.objects.count()
        context_data['hour_statistics_count'] = HourStatistics.objects.count()

        if not capabilities['any']:
            return context_data

        # Average of real consumption/return per hour.
        average_consumption_by_hour = dsmr_stats.services.average_consumption_by_hour(max_weeks_ago=4)

        context_data['avg_consumption_x'] = json.dumps(
            ['{}:00'.format(int(x['hour_start'])) for x in average_consumption_by_hour]
        )

        now = timezone.localtime(timezone.now())
        context_data['electricity_by_tariff_week'] = dsmr_stats.services.\
            electricity_tariff_percentage(start_date=now.date() - timezone.timedelta(days=7))

        context_data['electricity_by_tariff_month'] = dsmr_stats.services.\
            electricity_tariff_percentage(start_date=now.date() - relativedelta(months=1))

        graph_data = defaultdict(list)

        for current in average_consumption_by_hour:
            graph_data['x_hours'].append('{}:00'.format(int(current['hour_start'])))
            current['avg_electricity'] = (current['avg_electricity1'] + current['avg_electricity2']) / 2

            graph_data['avg_electricity_consumed'].append(
                float(dsmr_consumption.services.round_decimal(current['avg_electricity']))
            )

            if capabilities['electricity_returned']:
                current['avg_electricity_returned'] = (
                    current['avg_electricity1_returned'] + current['avg_electricity2_returned']
                ) / 2
                graph_data['avg_electricity_returned'].append(
                    float(dsmr_consumption.services.round_decimal(current['avg_electricity_returned']))
                )

            if capabilities['gas']:
                graph_data['avg_gas_consumption'].append(
                    float(dsmr_consumption.services.round_decimal(current['avg_gas']))
                )

        # We need the sums to calculate percentage.
        sums = {
            'avg_electricity_consumed': sum(graph_data['avg_electricity_consumed']),
            'avg_electricity_returned': sum(graph_data['avg_electricity_returned']),
            'avg_gas_consumption': sum(graph_data['avg_gas_consumption']),
        }

        # Map to percentages and JSON.
        for key, values in graph_data.items():
            try:
                current_sum = sums[key]
                values = [
                    float(dsmr_consumption.services.round_decimal(current / current_sum * 100))
                    for current
                    in values
                ]
            except (KeyError, ZeroDivisionError):
                pass

            context_data[key] = json.dumps(values)

        return context_data
