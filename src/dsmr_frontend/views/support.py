from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.utils.cache import patch_response_headers
from django.views import View
from django.views.generic.base import TemplateView

from dsmr_backend.tests.mixins import InterceptCommandStdoutMixin
from dsmr_datalogger.models.statistics import MeterStatistics
import dsmr_backend.services.backend
from dsmr_frontend.models.settings import FrontendSettings


class Support(LoginRequiredMixin, TemplateView):
    template_name = "dsmr_frontend/support.html"

    def get_context_data(self, **kwargs):
        context_data = super(Support, self).get_context_data(**kwargs)
        context_data[
            "monitoring_issues"
        ] = dsmr_backend.services.backend.request_monitoring_status()
        context_data["frontend_settings"] = FrontendSettings.get_solo()
        return context_data


class SupportXhrDebugInfo(LoginRequiredMixin, InterceptCommandStdoutMixin, View):
    def get(self, request):
        debug_dump = self._intercept_command_stdout("dsmr_debuginfo")

        response = JsonResponse(
            {
                "dump": debug_dump,
            }
        )
        patch_response_headers(response)

        return response


class SupportXhrLatestTelegram(LoginRequiredMixin, View):
    def get(self, request):
        meter_statistics = MeterStatistics.get_solo()

        response = JsonResponse(
            {
                "telegram": meter_statistics.latest_telegram,
            }
        )
        patch_response_headers(response)

        return response
