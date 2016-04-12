from django.views.generic.base import View, TemplateView
from django.http.response import StreamingHttpResponse

import dsmr_backend.services


class Deploy(TemplateView):
    """ Initial view rendered to load the iframe below. """
    template_name = 'dsmr_frontend/deploy.html'


class DeploymentStream(View):
    """ Actually performs the deploy, but yields stdout reponse to reflect progress. """
    def get(self, request, *args, **kwargs):
        return StreamingHttpResponse(dsmr_backend.services.deploy())
