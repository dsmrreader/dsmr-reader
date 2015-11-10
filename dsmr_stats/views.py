from django.views.generic.base import TemplateView

from dsmr_stats.models import DsmrReading


class Home(TemplateView):
    template_name = 'dsmr_stats/index.html'
    
    def get_context_data(self, **kwargs):
        print(DsmrReading.objects.all())
        return {
            'readings': DsmrReading.objects.all()
        }
