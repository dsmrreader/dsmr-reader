from collections import defaultdict
import json

from django.views.generic.base import TemplateView
from django.conf import settings
from django.utils import timezone

from dsmr_stats.models.statistics import DayStatistics
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings


class History(TemplateView):
    template_name = 'dsmr_frontend/history.html'

    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()

        context_data = super(History, self).get_context_data(**kwargs)
        context_data['usage'] = []
        context_data['days_ago'] = frontend_settings.recent_history_weeks * 7
        context_data['track_temperature'] = WeatherSettings.get_solo().track
        context_data['chart'] = defaultdict(list)

        CONSUMPTION_FIELDS = (
            'electricity1', 'electricity2', 'electricity1_returned', 'electricity2_returned', 'gas',
            'electricity1_cost', 'electricity2_cost', 'gas_cost', 'average_temperature'
        )

        now = timezone.now().astimezone(settings.LOCAL_TIME_ZONE)
        dates = (
            now - timezone.timedelta(days=n) for n in reversed(
                range(1, context_data['days_ago'] + 1)
            )
        )

        for current_day in dates:
            current_day = current_day.astimezone(settings.LOCAL_TIME_ZONE)

            try:
                day_stats = DayStatistics.objects.get(day=current_day)
            except DayStatistics.DoesNotExist:
                continue

            context_data['usage'].append(day_stats)
            context_data['chart']['days'].append(current_day.strftime("%a %d-%m"))

            for current_field in CONSUMPTION_FIELDS:
                context_data['chart'][current_field].append(float(
                    getattr(day_stats, current_field)
                ))

        for key, value in context_data['chart'].items():
            context_data['chart'][key] = json.dumps(value)

        return context_data
