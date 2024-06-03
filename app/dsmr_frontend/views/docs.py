from django.views.generic.base import TemplateView

from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin


class RedocApiDocs(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = "dsmr_frontend/docs/api/redoc.html"

    def get_context_data(self, **kwargs):
        context_data = super(RedocApiDocs, self).get_context_data(**kwargs)
        context_data.update(dict(schema_url="v2-api-openapi-schema"))
        return context_data
