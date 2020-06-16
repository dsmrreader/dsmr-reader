import decimal

from django.views.generic.base import TemplateView
from django.utils import timezone, formats

from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_frontend.views.archive import Archive
import dsmr_consumption.services
import dsmr_backend.services.backend
import dsmr_stats.services


class Compare(Archive):  # ConfigurableLoginRequiredMixin already in Archive
    template_name = 'dsmr_frontend/compare.html'


class CompareXhrSummary(ConfigurableLoginRequiredMixin, TemplateView):
    """ XHR view for comparing two statistics, HTML response. """
    template_name = 'dsmr_frontend/fragments/compare-xhr-statistics.html'

    def get_context_data(self, **kwargs):
        context_data = super(CompareXhrSummary, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.backend.get_capabilities()
        context_data['frontend_settings'] = FrontendSettings.get_solo()

        now = timezone.now().strftime(formats.get_format('DSMR_STRFTIME_DATE_FORMAT'))
        selected_base_datetime = timezone.make_aware(timezone.datetime.strptime(
            self.request.GET.get('base_date', now), formats.get_format('DSMR_STRFTIME_DATE_FORMAT')
        ))
        selected_comparison_datetime = timezone.make_aware(timezone.datetime.strptime(
            self.request.GET.get('comparison_date', now), formats.get_format('DSMR_STRFTIME_DATE_FORMAT')
        ))
        selected_level = self.request.GET.get('level', 'days')

        DATA_MAPPING = {
            'days': dsmr_stats.services.day_statistics,
            'months': dsmr_stats.services.month_statistics,
            'years': dsmr_stats.services.year_statistics,
        }

        base_data, base_count = DATA_MAPPING[selected_level](selected_base_datetime.date())
        comparison_data, comparison_count = DATA_MAPPING[selected_level](selected_comparison_datetime.date())
        diff_data = {}

        context_data['base_title'] = {
            'days': formats.date_format(selected_base_datetime.date(), 'DSMR_GRAPH_LONG_DATE_FORMAT'),
            'months': formats.date_format(selected_base_datetime.date(), 'DSMR_DATEPICKER_MONTH'),
            'years': selected_base_datetime.date().year,
        }[selected_level]

        context_data['comparison_title'] = {
            'days': formats.date_format(selected_comparison_datetime.date(), 'DSMR_GRAPH_LONG_DATE_FORMAT'),
            'months': formats.date_format(selected_comparison_datetime.date(), 'DSMR_DATEPICKER_MONTH'),
            'years': selected_comparison_datetime.date().year,
        }[selected_level]

        # Remove unused keys.
        unused_keys = []

        for k in base_data.keys():
            if k in ('temperature_avg', 'temperature_max', 'temperature_min') or 'cost' in k:
                unused_keys.append(k)

        base_data = {k: v for k, v in base_data.items() if k not in unused_keys}
        comparison_data = {k: v for k, v in comparison_data.items() if k not in unused_keys}

        # Calculate percentages of selection compared to base, as difference in percent.
        for k in base_data.keys():
            try:
                diff_data[k] = 100 - (comparison_data[k] / base_data[k] * 100)
            except (TypeError, decimal.InvalidOperation, decimal.DivisionByZero):
                diff_data[k] = 0

            diff_data[k] = diff_data[k] * -1  # If the result above is 10%, then we'd like to display it as -10% usage.
            diff_data[k] = dsmr_consumption.services.round_decimal(diff_data[k])

        context_data['diff'] = diff_data
        context_data['base'] = base_data
        context_data['comparison'] = comparison_data
        context_data['data_count'] = dict(base=base_count, comparison=comparison_count)
        return context_data
