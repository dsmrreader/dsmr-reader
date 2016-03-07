from django.views.generic.base import TemplateView
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_backend.services


class Statistics(TemplateView):
    template_name = 'dsmr_frontend/statistics.html'

    def get_context_data(self, **kwargs):
        context_data = super(Statistics, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()

        today = timezone.localtime(timezone.now()).date()

        context_data['total_reading_count'] = DsmrReading.objects.count()
        context_data['datalogger_settings'] = DataloggerSettings.get_solo()
        context_data['meter_statistics'] = MeterStatistics.get_solo()

        try:
            context_data['latest_reading'] = DsmrReading.objects.all().order_by('-pk')[0]
            context_data['first_reading'] = DsmrReading.objects.all().order_by('pk')[0]
        except IndexError:
            return context_data

        try:
            context_data['energy_prices'] = EnergySupplierPrice.objects.by_date(today)
        except EnergySupplierPrice.DoesNotExist:
            pass

        return context_data
