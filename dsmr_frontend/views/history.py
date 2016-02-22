from collections import defaultdict
import json

from django.views.generic.base import TemplateView
from django.utils import formats
from django.utils import timezone

from dsmr_stats.models.statistics import DayStatistics
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.note import Note


class History(TemplateView):
    template_name = 'dsmr_frontend/history.html'

    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()

        context_data = super(History, self).get_context_data(**kwargs)
        context_data['usage'] = []
        context_data['days_ago'] = frontend_settings.recent_history_weeks * 7
        context_data['track_temperature'] = WeatherSettings.get_solo().track
        context_data['chart'] = defaultdict(list)
        context_data['day_format'] = 'DSMR_GRAPH_LONG_DATE_FORMAT'

        CONSUMPTION_FIELDS = (
            'electricity1', 'electricity2', 'electricity1_returned', 'electricity2_returned', 'gas',
            'electricity1_cost', 'electricity2_cost', 'gas_cost', 'total_cost', 'average_temperature'
        )

        now = timezone.localtime(timezone.now())
        dates = (
            now - timezone.timedelta(days=n) for n in reversed(
                range(1, context_data['days_ago'] + 1)
            )
        )

        for current_day in dates:
            current_day = current_day

            try:
                day_stats = DayStatistics.objects.get(day=current_day).__dict__
            except DayStatistics.DoesNotExist:
                continue

            # Add any notes, as the model has been converted to a dict above.
            day_stats['notes'] = Note.objects.filter(day=current_day).values_list('description', flat=True)

            context_data['usage'].append(day_stats)
            context_data['chart']['days'].append(
                formats.date_format(current_day, 'DSMR_GRAPH_SHORT_DATE_FORMAT')
            )

            for current_field in CONSUMPTION_FIELDS:
                context_data['chart'][current_field].append(float(day_stats[current_field]))

        for key, value in context_data['chart'].items():
            context_data['chart'][key] = json.dumps(value)

        return context_data
