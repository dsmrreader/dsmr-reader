from django.http import JsonResponse
from django.utils import formats
from django.views.generic.base import TemplateView, View

from dsmr_backend.dto import Capability
from dsmr_frontend.forms import TrendsPeriodForm
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
        context_data['datepicker_locale_format'] = formats.get_format('DSMR_DATEPICKER_LOCALE_FORMAT')
        context_data['datepicker_date_format'] = 'DSMR_DATEPICKER_DATE_FORMAT'

        day_statistics = DayStatistics.objects.all().order_by('day')

        try:
            context_data['start_date'] = day_statistics[0].day
            context_data['end_date'] = day_statistics.order_by('-day')[0].day
        except IndexError:
            pass

        return context_data


class TrendsXhrAvgConsumption(ConfigurableLoginRequiredMixin, View):
    """ XHR view for fetching average consumption, in JSON. """

    def get(self, request):
        form = TrendsPeriodForm(request.GET)

        if not form.is_valid():
            return JsonResponse(dict(errors=form.errors), status=400)

        capabilities = dsmr_backend.services.backend.get_capabilities()
        average_consumption_by_hour = dsmr_stats.services.average_consumption_by_hour(
            start=form.cleaned_data['start_date'],
            end=form.cleaned_data['end_date'],
        )
        data = {
            'electricity': [],
            'electricity_returned': [],
            'gas': [],
        }

        for current in average_consumption_by_hour:
            hour_start = '{}:00 - {}:00'.format(int(current['hour_start']), int(current['hour_start']) + 1)

            avg_electricity = (current['avg_electricity1'] + current['avg_electricity2']) / 2

            textColor = 'black'
            if form.cleaned_data['dark_theme'] == 'true':
               textColor = 'rgba(255, 255, 255, 0.6)'

            data['electricity'].append({
                'name': hour_start,
                'value': float(dsmr_consumption.services.round_decimal(avg_electricity, decimal_count=5)),
                'label': {
                    'color': textColor
                }
            })

            if capabilities[Capability.ELECTRICITY_RETURNED]:
                avg_electricity_returned = (
                    current['avg_electricity1_returned'] + current['avg_electricity2_returned']
                ) / 2
                data['electricity_returned'].append({
                    'name': hour_start,
                    'value': float(dsmr_consumption.services.round_decimal(avg_electricity_returned, decimal_count=5)),
                    'label': {
                        'color': textColor
                    }
                })

            if capabilities[Capability.GAS]:
                data['gas'].append({
                    'name': hour_start,
                    'value': float(dsmr_consumption.services.round_decimal(current['avg_gas'], decimal_count=5)),
                    'label': {
                        'color': textColor
                    }
                })

        return JsonResponse(data)


class TrendsXhrElectricityByTariff(ConfigurableLoginRequiredMixin, View):
    """ XHR view for fetching electricity consumption by tariff, in JSON. """

    def get(self, request):
        form = TrendsPeriodForm(request.GET)

        if not form.is_valid():
            return JsonResponse(dict(errors=form.errors), status=400)

        capabilities = dsmr_backend.services.backend.get_capabilities()
        frontend_settings = FrontendSettings.get_solo()
        translation_mapping = {
            'electricity1': frontend_settings.tariff_1_delivered_name.capitalize(),
            'electricity2': frontend_settings.tariff_2_delivered_name.capitalize(),
        }
        result = {}

        textColor = 'black'
        if form.cleaned_data['dark_theme'] == 'true':
            textColor = 'rgba(255, 255, 255, 0.6)'

        if not capabilities[Capability.ANY] or not DayStatistics.objects.exists():
            return JsonResponse(result)

        result['data'] = [
            {
                'name': translation_mapping[k],
                'value': v,
                'label': {
                    'color': textColor
                }
            }
            for k, v in
            dsmr_stats.services.electricity_tariff_percentage(
                start=form.cleaned_data['start_date'],
                end=form.cleaned_data['end_date'],
            ).items()
        ]

        return JsonResponse(result)
