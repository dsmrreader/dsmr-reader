import random
import json

from django.views.generic.base import TemplateView
from django.conf import settings
from django.utils import timezone

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
import dsmr_consumption.services
import dsmr_stats.services


class Statistics(TemplateView):
    template_name = 'dsmr_frontend/statistics.html'

    def get_context_data(self, **kwargs):
        context_data = super(Statistics, self).get_context_data(**kwargs)
        today = timezone.now().astimezone(settings.LOCAL_TIME_ZONE).date()
        context_data['latest_reading'] = DsmrReading.objects.all().order_by('-pk')[0]
        context_data['first_reading'] = DsmrReading.objects.all().order_by('pk')[0]
        context_data['total_reading_count'] = DsmrReading.objects.count()

        # Average of 'currently delivered' in Watt.
        avg_electricity_delivered_per_hour = dsmr_consumption.services.average_electricity_delivered_by_hour()
        context_data['avg_electricity_delivered'] = json.dumps(
            [
                {
                    'value': float(dsmr_consumption.services.round_decimal(x['avg_delivered'] * 1000)),
                    'color': str(self._hour_to_color(x['hour'], 0x3D9970)),
                    'label': '{}:00'.format(int(x['hour'])),
                    'highlight': '#5AD3D1',
                }
                for x in avg_electricity_delivered_per_hour
            ]
        )

        # Average of real usage per hour, in kWh,
        average_consumption_by_hour = dsmr_stats.services.average_consumption_by_hour()
        context_data['avg_consumption_x'] = json.dumps(
            ['{}:00'.format(int(x['hour_start'])) for x in average_consumption_by_hour]
        )

        # @TODO: This should be packed into a helper or something.
        context_data['avg_electricity1_consumption'] = json.dumps(
            [
                {
                    'value': float(dsmr_consumption.services.round_decimal(x['avg_electricity1'])),
                    'color': str(self._hour_to_color(x['hour_start'], 0xF05050)),
                    'label': '{}:00'.format(int(x['hour_start'])),
                    'highlight': '#5AD3D1',
                }
                for x in average_consumption_by_hour
            ]
        )

        context_data['avg_electricity2_consumption'] = json.dumps(
            [
                {
                    'value': float(dsmr_consumption.services.round_decimal(x['avg_electricity2'])),
                    'color': self._hour_to_color(x['hour_start'], 0xF05050),
                    'label': '{}:00'.format(int(x['hour_start'])),
                    'highlight': '#5AD3D1',
                }
                for x in average_consumption_by_hour
            ]
        )

        context_data['avg_gas_consumption'] = json.dumps(
            [
                {
                    'value': float(dsmr_consumption.services.round_decimal(x['avg_gas'])),
                    'color': self._hour_to_color(x['hour_start'], 0xFF851B),
                    'label': '{}:00'.format(int(x['hour_start'])),
                    'highlight': '#5AD3D1',
                }
                for x in average_consumption_by_hour
            ]
        )

        try:
            context_data['energy_prices'] = EnergySupplierPrice.objects.by_date(today)
        except EnergySupplierPrice.DoesNotExist:
            pass

        return context_data

    def _hour_to_color(self, hour, offset=0):
        """ A little help to render 'random' colors, making the graphs look less dull. """
        # Offset 4000000 = purple.
        return '#%06x' % int(hour * 5 + int(offset))
