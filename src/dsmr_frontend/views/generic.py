from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.cache import patch_response_headers
from django.views.generic.base import RedirectView
from django.views.generic.base import View
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from typing import Optional

import dsmr_consumption.services
from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin


class XhrHeader(ConfigurableLoginRequiredMixin, View):
    """XHR view for fetching the dashboard header, displaying latest readings and price estimate, JSON response."""

    def get(self, request):
        data = dsmr_consumption.services.live_electricity_consumption()

        if data and data["timestamp"]:
            data["timestamp"] = str(naturaltime(data["timestamp"]))

        response = JsonResponse(data)
        patch_response_headers(response)

        return response


class StatusRedirectView(RedirectView):
    permanent = False
    pattern_name = "frontend:about"


class ReadTheDocsRedirectView(RedirectView):
    permanent = False
    subpage: Optional[str] = None
    branch = settings.DSMRREADER_MAIN_BRANCH
    url: Optional[str] = None

    def get(self, request, *args, **kwargs):
        self.url = "https://dsmr-reader.readthedocs.io/en/{}/{}".format(self.branch, self.subpage)
        return super(ReadTheDocsRedirectView, self).get(request, *args, **kwargs)


class ChangelogRedirect(ReadTheDocsRedirectView):
    subpage = "reference/changelog/"


class DocsRedirect(ReadTheDocsRedirectView):
    subpage = ""


class HealthCheck(View):
    def get(self, request):
        return HttpResponse(status=200)
