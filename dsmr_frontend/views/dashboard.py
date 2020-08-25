from django.views.generic.base import TemplateView
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_frontend.models.message import Notification
from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_consumption.services
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
        context_data['django_date_format'] = 'DSMR_GRAPH_LONG_DATE_FORMAT'

        try:
            latest_electricity = ElectricityConsumption.objects.all().order_by('-read_at')[0]
        except IndexError:
            # Don't even bother when no data available.
            return context_data

        context_data['consumption'] = dsmr_consumption.services.day_consumption(
            day=timezone.localtime(latest_electricity.read_at).date()
        )
        month_statistics, days_in_month = dsmr_stats.services.month_statistics(
            target_date=timezone.localtime(timezone.now()).date()
        )
        context_data['month_statistics'] = month_statistics
        context_data['days_in_month'] = days_in_month

        return context_data
