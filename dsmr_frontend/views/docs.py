from django.views.generic.base import TemplateView


class ApiDocs(TemplateView):
    template_name = 'dsmr_frontend/docs/api.html'
