import json

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse
from django.utils import formats, timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.reading import DsmrReading, MeterStatistics
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_frontend.models.message import Notification
import dsmr_consumption.services
import dsmr_backend.services
import dsmr_stats.services


class Dashboard(TemplateView):
    template_name = 'dsmr_frontend/dashboard.html'
    electricity_max = 30  # Minutes or readings.
    gas_max = 25  # Hours.
    temperature_max = gas_max

    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()
        weather_settings = WeatherSettings.get_solo()
        context_data = super(Dashboard, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['frontend_settings'] = frontend_settings
        context_data['track_temperature'] = weather_settings.track
        context_data['notifications'] = Notification.objects.unread()

        electricity = ElectricityConsumption.objects.all().order_by('read_at')
        gas = GasConsumption.objects.all().order_by('read_at')
        temperature = TemperatureReading.objects.all().order_by('read_at')

        # User might want to sort things backwards.
        if frontend_settings.reverse_dashboard_graphs:
            electricity = electricity.reverse()[:self.electricity_max]
            gas = gas.reverse()[:self.gas_max]
            temperature = temperature.reverse()[:self.temperature_max]
        else:
            # We can't slice using negative offsets, so we should fetch a (quick) count first. However, counts tend to
            # be slow, so we need to filter first by, let's say, the last week.
            electricity = electricity.filter(read_at__gt=timezone.now() - timezone.timedelta(days=7))

            electricity_offset = max(0, electricity.count() - self.electricity_max)
            gas_offset = max(0, gas.count() - self.gas_max)
            temperature_offset = max(0, temperature.count() - self.temperature_max)

            electricity = electricity[electricity_offset:]
            gas = gas[gas_offset:]
            temperature = temperature[temperature_offset:]

        context_data['electricity_x'] = json.dumps(
            [formats.date_format(
                timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_TIME_FORMAT'
            ) for x in electricity]
        )
        context_data['electricity_y'] = json.dumps(
            [float(x.currently_delivered * 1000) for x in electricity]
        )
        context_data['electricity_returned_y'] = json.dumps(
            [float(x.currently_returned * 1000) for x in electricity]
        )

        context_data['gas_x'] = json.dumps(
            [formats.date_format(
                timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_TIME_FORMAT'
            ) for x in gas]
        )
        context_data['gas_y'] = json.dumps(
            [float(x.currently_delivered) for x in gas]
        )

        if weather_settings.track:
            context_data['temperature_x'] = json.dumps(
                [formats.date_format(
                    timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_TIME_FORMAT'
                ) for x in temperature]
            )
            context_data['temperature_y'] = json.dumps(
                [float(x.degrees_celcius) for x in temperature]
            )

        try:
            latest_electricity = ElectricityConsumption.objects.all().order_by('-read_at')[0]
        except IndexError:
            # Don't even bother when no data available.
            return context_data

        context_data['consumption'] = dsmr_consumption.services.day_consumption(
            day=timezone.localtime(latest_electricity.read_at).date()
        )
        today = timezone.localtime(timezone.now()).date()
        context_data['month_statistics'] = dsmr_stats.services.month_statistics(target_date=today)
        return context_data


class DashboardXhrHeader(View):
    """ XHR view for fetching the dashboard header, displaying latest readings and price estimate, JSON response. """
    def get(self, request):
        data = {}

        try:
            latest_reading = DsmrReading.objects.all().order_by('-pk')[0]
        except IndexError:
            # Don't even bother when no data available.
            return HttpResponse(json.dumps(data), content_type='application/json')

        data['timestamp'] = naturaltime(latest_reading.timestamp)
        data['currently_delivered'] = int(latest_reading.electricity_currently_delivered * 1000)
        data['currently_returned'] = int(latest_reading.electricity_currently_returned * 1000)

        try:
            # This WILL fail when we either have no prices at all or conflicting ranges.
            prices = EnergySupplierPrice.objects.by_date(target_date=timezone.now().date())
        except (EnergySupplierPrice.DoesNotExist, EnergySupplierPrice.MultipleObjectsReturned):
            return HttpResponse(json.dumps(data), content_type='application/json')

        # We need to current tariff to get the right price.
        tariff = MeterStatistics.get_solo().electricity_tariff
        currently_delivered = latest_reading.electricity_currently_delivered
        cost_per_hour = None

        tariff_map = {
            1: prices.electricity_1_price,
            2: prices.electricity_2_price,
        }

        try:
            cost_per_hour = currently_delivered * tariff_map[tariff]
        except KeyError:
            pass
        else:
            data['latest_electricity_cost'] = formats.number_format(
                dsmr_consumption.services.round_decimal(cost_per_hour)
            )

        return HttpResponse(json.dumps(data), content_type='application/json')
