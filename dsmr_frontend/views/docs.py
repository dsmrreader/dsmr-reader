from django.views.generic.base import TemplateView

from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin


class ApiDocs(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/docs/api.html'
