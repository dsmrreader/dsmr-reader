from django.views.generic.base import TemplateView

from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.settings import StatsSettings
from dsmr_weather.models.settings import WeatherSettings


class Status(TemplateView):
    template_name = 'dsmr_frontend/status.html'

    def get_context_data(self, **kwargs):
        context_data = super(Status, self).get_context_data(**kwargs)
        context_data['consumption_settings'] = ConsumptionSettings.get_solo()
        context_data['datalogger_settings'] = DataloggerSettings.get_solo()
        context_data['frontend_settings'] = FrontendSettings.get_solo()
        context_data['stats_settings'] = StatsSettings.get_solo()
        context_data['weather_settings'] = WeatherSettings.get_solo()
        return context_data
