import json

from django.views.generic.base import View, TemplateView
from django.http.response import HttpResponse

import dsmr_backend.services


class Status(TemplateView):
    template_name = 'dsmr_frontend/status.html'

    def get_context_data(self, **kwargs):
        context_data = super(Status, self).get_context_data(**kwargs)
        context_data['status'] = dsmr_backend.services.status_info()
        context_data['capabilities'] = context_data['status']['capabilities']
        return context_data


class XhrUpdateChecker(View):
    """ XHR view performing a version check versus Github. """
    def get(self, request):
        return HttpResponse(
            json.dumps({'update_available': not dsmr_backend.services.is_latest_version()}),
            content_type='application/json'
        )
