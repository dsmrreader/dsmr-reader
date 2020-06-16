from django.http import JsonResponse
from django.views.generic.base import TemplateView, View
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
import dsmr_consumption.services
import dsmr_backend.services.backend
import dsmr_stats.services


class Trends(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/trends.html'

    def get_context_data(self, **kwargs):
        capabilities = dsmr_backend.services.backend.get_capabilities()

        context_data = super(Trends, self).get_context_data(**kwargs)
        context_data['capabilities'] = capabilities
        context_data['frontend_settings'] = FrontendSettings.get_solo()
        context_data['has_statistics'] = DayStatistics.objects.exists() and HourStatistics.objects.exists()

        return context_data


class TrendsXhrAvgConsumption(ConfigurableLoginRequiredMixin, View):
    """ XHR view for fetching average consumption, in JSON. """
    def get(self, request):  # noqa: C901
        data = {
            'electricity': [],
            'electricity_returned': [],
            'gas': [],
        }

        capabilities = dsmr_backend.services.backend.get_capabilities()
        average_consumption_by_hour = dsmr_stats.services.average_consumption_by_hour(max_weeks_ago=4)

        for current in average_consumption_by_hour:
            hour_start = '{}:00 - {}:00'.format(int(current['hour_start']), int(current['hour_start']) + 1)

            avg_electricity = (current['avg_electricity1'] + current['avg_electricity2']) / 2
            data['electricity'].append({
                'name': hour_start,
                'value': float(dsmr_consumption.services.round_decimal(avg_electricity))
            })

            if capabilities['electricity_returned']:
                avg_electricity_returned = (
                    current['avg_electricity1_returned'] + current['avg_electricity2_returned']
                ) / 2
                data['electricity_returned'].append({
                    'name': hour_start,
                    'value': float(dsmr_consumption.services.round_decimal(avg_electricity_returned))
                })

            if capabilities['gas']:
                data['gas'].append({
                    'name': hour_start,
                    'value': float(dsmr_consumption.services.round_decimal(current['avg_gas']))
                })

        return JsonResponse(data)


class TrendsXhrElectricityByTariff(ConfigurableLoginRequiredMixin, View):
    """ XHR view for fetching electricity consumption by tariff, in JSON. """
    def get(self, request):  # noqa: C901
        capabilities = dsmr_backend.services.backend.get_capabilities()
        frontend_settings = FrontendSettings.get_solo()
        data = {}
        translation_mapping = {
            'electricity1': frontend_settings.tariff_1_delivered_name,
            'electricity2': frontend_settings.tariff_2_delivered_name,
        }

        if not capabilities['any'] or not DayStatistics.objects.exists():
            return JsonResponse(data)

        now = timezone.localtime(timezone.now())
        week_date = now.date() - timezone.timedelta(days=7)
        month_date = now.date() - relativedelta(months=1)

        data['week'] = [
            {'name': translation_mapping[k], 'value': v}
            for k, v in
            dsmr_stats.services.electricity_tariff_percentage(start_date=week_date).items()
        ]
        data['month'] = [
            {'name': translation_mapping[k], 'value': v}
            for k, v in
            dsmr_stats.services.electricity_tariff_percentage(start_date=month_date).items()
        ]

        return JsonResponse(data)
