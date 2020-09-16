from django.views.generic.base import TemplateView

import dsmr_backend.services.backend
from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin


class Status(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/status.html'

    def get_context_data(self, **kwargs):
        context_data = super(Status, self).get_context_data(**kwargs)
        context_data['monitoring_issues'] = dsmr_backend.services.backend.request_monitoring_status()
        return context_data
