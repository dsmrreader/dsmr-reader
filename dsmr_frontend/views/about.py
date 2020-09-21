from django.views.generic.base import TemplateView

from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin


class About(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/about.html'
