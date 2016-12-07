import json

from django.views.generic.base import View, TemplateView
from django.http.response import HttpResponse
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.reading import DsmrReading
import dsmr_backend.services


class Status(TemplateView):
    template_name = 'dsmr_frontend/status.html'

    def get_context_data(self, **kwargs):
        context_data = super(Status, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['unprocessed_readings'] = DsmrReading.objects.unprocessed().count()

        try:
            context_data['latest_reading'] = DsmrReading.objects.all().order_by('-pk')[0]
            context_data['first_reading'] = DsmrReading.objects.all().order_by('pk')[0]
        except IndexError:
            pass
        else:
            context_data['delta_since_latest_reading'] = (
                timezone.now() - context_data['latest_reading'].timestamp
            ).seconds

        if context_data['capabilities']['electricity']:
            context_data['latest_ec'] = ElectricityConsumption.objects.all().order_by('-pk')[0]
            context_data['delta_since_latest_ec'] = (timezone.now() - context_data['latest_ec'].read_at).seconds

        if context_data['capabilities']['gas']:
            context_data['latest_gc'] = GasConsumption.objects.all().order_by('-pk')[0]
            context_data['delta_since_latest_gc'] = (timezone.now() - context_data['latest_gc'].read_at).seconds

        return context_data


class XhrUpdateChecker(View):
    """ XHR view performing a version check versus Github. """
    def get(self, request):
        return HttpResponse(
            json.dumps({'update_available': not dsmr_backend.services.is_latest_version()}),
            content_type='application/json'
        )
