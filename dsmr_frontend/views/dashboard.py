from django.views.generic.base import TemplateView

from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_frontend.models.message import Notification
from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_backend.services.backend
import dsmr_stats.services


class Dashboard(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/dashboard.html'

    def get_context_data(self, **kwargs):
        context_data = super(Dashboard, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.backend.get_capabilities()
        context_data['datalogger_settings'] = DataloggerSettings.get_solo()
        context_data['frontend_settings'] = FrontendSettings.get_solo()
        context_data['notification_count'] = Notification.objects.unread().count()
        context_data['today_date_format'] = 'DSMR_GRAPH_LONG_DATE_FORMAT'
        context_data['month_date_format'] = 'DSMR_DATEPICKER_MONTH'
        context_data['year_date_format'] = 'DSMR_DATEPICKER_YEAR'
        context_data['period_totals'] = dsmr_stats.services.period_totals()

        return context_data
