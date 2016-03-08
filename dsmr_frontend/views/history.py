from collections import defaultdict
from datetime import time
import json

from django.views.generic.base import TemplateView
from django.utils import formats
from django.utils import timezone

from dsmr_stats.models.statistics import DayStatistics
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.note import Note
import dsmr_backend.services
import dsmr_stats.services


class History(TemplateView):
    template_name = 'dsmr_frontend/history.html'

    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()

        context_data = super(History, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['usage'] = []
        context_data['days_ago'] = frontend_settings.recent_history_weeks * 7
        context_data['track_temperature'] = WeatherSettings.get_solo().track
        context_data['chart'] = defaultdict(list)
        context_data['day_format'] = 'DSMR_GRAPH_LONG_DATE_FORMAT'

        CONSUMPTION_FIELDS = (
            'electricity1', 'electricity2', 'electricity1_returned', 'electricity2_returned', 'gas',
            'electricity1_cost', 'electricity2_cost', 'gas_cost', 'total_cost', 'average_temperature'
        )

        today = timezone.localtime(timezone.now()).date()
        now = timezone.datetime.combine(today, time.min)

        start = now - timezone.timedelta(days=context_data['days_ago'])
        dates = (
            now - timezone.timedelta(days=n) for n in reversed(
                range(1, context_data['days_ago'] + 1)
            )
        )

        passed_days = DayStatistics.objects.filter(day__gte=start)

        for current_day_statistics in passed_days:
            day_stats = current_day_statistics.__dict__

            # Add any notes, as the model has been converted to a dict above.
            day_stats['notes'] = Note.objects.filter(day=current_day_statistics.day).values_list('description', flat=True)

            context_data['usage'].append(day_stats)
            context_data['chart']['days'].append(
                formats.date_format(current_day_statistics.day, 'DSMR_GRAPH_SHORT_DATE_FORMAT')
            )

            for current_field in CONSUMPTION_FIELDS:
                context_data['chart'][current_field].append(float(day_stats[current_field]))

        for key, value in context_data['chart'].items():
            context_data['chart'][key] = json.dumps(value)

        dates = list(dates)
        context_data['statistics_summary'] = dsmr_stats.services.range_statistics(
            start=now - timezone.timedelta(days=context_data['days_ago']),
            end=now
        )

        return context_data
