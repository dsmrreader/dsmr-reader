from django.views.generic.edit import FormView

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_frontend.forms import ExportForm


class Export(FormView):
    template_name = 'dsmr_frontend/export.html'
    form_class = ExportForm

#     def get_context_data(self, **kwargs):
#         context_data = super(Export, self).get_context_data(**kwargs)
# 
#         return context_data
