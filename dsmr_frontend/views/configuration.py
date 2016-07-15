from django.views.generic.base import TemplateView, View
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils import timezone

from dsmr_api.models import APISettings
from dsmr_consumption.models.settings import ConsumptionSettings
from dsmr_datalogger.models.settings import DataloggerSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_weather.models.settings import WeatherSettings
from dsmr_backup.models.settings import BackupSettings, DropboxSettings
from dsmr_mindergas.models.settings import MinderGasSettings


class Configuration(TemplateView):
    template_name = 'dsmr_frontend/configuration.html'

    def get_context_data(self, **kwargs):
        context_data = super(Configuration, self).get_context_data(**kwargs)
        context_data['api_settings'] = APISettings.get_solo()
        context_data['consumption_settings'] = ConsumptionSettings.get_solo()
        context_data['datalogger_settings'] = DataloggerSettings.get_solo()
        context_data['frontend_settings'] = FrontendSettings.get_solo()
        context_data['weather_settings'] = WeatherSettings.get_solo()
        context_data['backup_settings'] = BackupSettings.get_solo()
        context_data['dropbox_settings'] = DropboxSettings.get_solo()
        context_data['mindergas_settings'] = MinderGasSettings.get_solo()
        return context_data


class ForceBackup(View):
    """ Alters the backup settings, forcing the application to create a (new) backup right away. """
    def post(self, request):
        backup_settings = BackupSettings.get_solo()
        backup_settings.latest_backup = timezone.now() - timezone.timedelta(days=7)
        backup_settings.save()

        return redirect(reverse('frontend:configuration'))
