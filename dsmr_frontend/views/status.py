from django.views.generic.base import TemplateView

import dsmr_backend.services.backend
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin


class Status(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/status.html'

    def get_context_data(self, **kwargs):
        context_data = super(Status, self).get_context_data(**kwargs)
        context_data['monitoring_issues'] = dsmr_backend.services.backend.request_monitoring_status()

        try:
            latest_reading = DsmrReading.objects.all().order_by('-pk')[0]
        except IndexError:
            pass
        else:
            context_data['latest_reading'] = latest_reading

        return context_data
