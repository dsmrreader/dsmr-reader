from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views import View
from django.views.generic.base import TemplateView

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin
import dsmr_backend.services.backend
from dsmr_frontend.models.settings import FrontendSettings


class About(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/about.html'

    def get_context_data(self, **kwargs):
        context_data = super(About, self).get_context_data(**kwargs)
        context_data['monitoring_issues'] = dsmr_backend.services.backend.request_monitoring_status()
        context_data['frontend_settings'] = FrontendSettings.get_solo()
        return context_data


class AboutXhrUpdateCheck(ConfigurableLoginRequiredMixin, View):
    def get(self, request):
        return JsonResponse({
            'is_latest_version': dsmr_backend.services.backend.is_latest_version(),
        })


class AboutXhrDebugInfo(LoginRequiredMixin, InterceptCommandStdoutMixin, View):
    def get(self, request):
        debug_dump = self._intercept_command_stdout('dsmr_debuginfo')

        return JsonResponse({
            'dump': debug_dump,
        })
