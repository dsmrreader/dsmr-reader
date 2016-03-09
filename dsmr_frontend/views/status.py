from django.views.generic.base import TemplateView

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_backend.services


class Status(TemplateView):
    template_name = 'dsmr_frontend/status.html'

    def get_context_data(self, **kwargs):
        context_data = super(Status, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['total_reading_count'] = DsmrReading.objects.count()
        context_data['unprocessed_readings'] = DsmrReading.objects.unprocessed().count()

        try:
            context_data['latest_reading'] = DsmrReading.objects.all().order_by('-pk')[0]
            context_data['first_reading'] = DsmrReading.objects.all().order_by('pk')[0]
        except IndexError:
            pass

        if context_data['capabilities']['electricity']:
            context_data['latest_ec'] = ElectricityConsumption.objects.all().order_by('-pk')[0]

        if context_data['capabilities']['gas']:
            context_data['latest_gc'] = GasConsumption.objects.all().order_by('-pk')[0]

        return context_data
