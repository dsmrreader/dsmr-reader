from django.http import JsonResponse
from django.views.generic.base import View, TemplateView

import dsmr_backend.services.backend


class Status(TemplateView):
    template_name = 'dsmr_frontend/status.html'

    def get_context_data(self, **kwargs):
        context_data = super(Status, self).get_context_data(**kwargs)
        context_data['status'] = dsmr_backend.services.backend.status_info()
        context_data['capabilities'] = context_data['status']['capabilities']
        return context_data


class XhrUpdateChecker(View):
    """ XHR view performing a version check versus Github. """
    def get(self, request):
        return JsonResponse({
            'update_available': not dsmr_backend.services.backend.is_latest_version()
        })
