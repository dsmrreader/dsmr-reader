import json

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.views.generic.base import TemplateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.utils import formats, timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_frontend.forms import DashboardGraphForm, DashboardNotificationReadForm
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_frontend.models.message import Notification
from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_consumption.services
import dsmr_backend.services
import dsmr_stats.services


class Dashboard(TemplateView):
    template_name = 'dsmr_frontend/dashboard.html'

    def get_context_data(self, **kwargs):
        frontend_settings = FrontendSettings.get_solo()
        weather_settings = WeatherSettings.get_solo()
        context_data = super(Dashboard, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['datalogger_settings'] = DataloggerSettings.get_solo()
        context_data['frontend_settings'] = frontend_settings
        context_data['track_temperature'] = weather_settings.track
        context_data['notifications'] = Notification.objects.unread()

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

        latest_timestamp = latest_reading.timestamp

        # In case the smart meter is running a clock in the future.
        if latest_timestamp > timezone.now():
            latest_timestamp = timezone.now()

        data['timestamp'] = naturaltime(latest_timestamp)
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
            1: prices.electricity_delivered_1_price,
            2: prices.electricity_delivered_2_price,
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


class DashboardXhrConsumption(TemplateView):
    """ XHR view for fetching consumption, HTML response. """
    template_name = 'dsmr_frontend/fragments/dashboard-xhr-consumption.html'

    def get_context_data(self, **kwargs):
        context_data = super(DashboardXhrConsumption, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['frontend_settings'] = FrontendSettings.get_solo()

        try:
            latest_electricity = ElectricityConsumption.objects.all().order_by('-read_at')[0]
        except IndexError:
            # Don't even bother when no data available.
            return context_data

        context_data['consumption'] = dsmr_consumption.services.day_consumption(
            day=timezone.localtime(latest_electricity.read_at).date()
        )

        return context_data


class DashboardXhrGraphs(View):
    """ XHR view for fetching all dashboard data. """
    MAX_ITEMS = 30

    def get(self, request):
        data = {}
        data['capabilities'] = dsmr_backend.services.get_capabilities()

        form = DashboardGraphForm(request.GET)

        if not form.is_valid():
            return HttpResponseBadRequest(form.errors)

        # Optimize queries for large datasets by restricting the data to the last week in the first place.
        base_timestamp = timezone.now() - timezone.timedelta(days=7)

        electricity = ElectricityConsumption.objects.filter(read_at__gt=base_timestamp).order_by('-read_at')
        gas = GasConsumption.objects.filter(read_at__gt=base_timestamp).order_by('-read_at')
        temperature = TemperatureReading.objects.filter(read_at__gt=base_timestamp).order_by('-read_at')

        # Apply any offset requested by the user.
        electricity_offset = form.cleaned_data.get('electricity_offset')
        electricity = electricity[electricity_offset:electricity_offset + self.MAX_ITEMS]

        gas_offset = form.cleaned_data.get('gas_offset')
        gas = gas[gas_offset:gas_offset + self.MAX_ITEMS]

        temperature = temperature[:self.MAX_ITEMS]

        # Reverse all sets gain.
        electricity = electricity[::-1]
        gas = gas[::-1]
        temperature = temperature[::-1]

        # By default we only display the time, scrolling should enable a more verbose x-axis.
        graph_x_format_electricity = 'DSMR_GRAPH_SHORT_TIME_FORMAT'
        graph_x_format_gas = 'DSMR_GRAPH_SHORT_TIME_FORMAT'

        if electricity_offset > 0:
            graph_x_format_electricity = 'DSMR_GRAPH_LONG_TIME_FORMAT'

        if gas_offset > 0:
            graph_x_format_gas = 'DSMR_GRAPH_LONG_TIME_FORMAT'

        data['electricity_x'] = [
            formats.date_format(
                timezone.localtime(x.read_at), graph_x_format_electricity
            )
            for x in electricity
        ]
        data['electricity_y'] = [float(x.currently_delivered * 1000) for x in electricity]
        data['electricity_returned_y'] = [float(x.currently_returned * 1000) for x in electricity]

        data['gas_x'] = [
            formats.date_format(
                timezone.localtime(x.read_at), graph_x_format_gas
            ) for x in gas
        ]
        data['gas_y'] = [float(x.currently_delivered) for x in gas]

        # Some users have multiple phases installed.
        if DataloggerSettings.get_solo().track_phases and data['capabilities']['multi_phases']:
            data['phases_l1_y'] = self._parse_phases_data(electricity, 'phase_currently_delivered_l1')
            data['phases_l2_y'] = self._parse_phases_data(electricity, 'phase_currently_delivered_l2')
            data['phases_l3_y'] = self._parse_phases_data(electricity, 'phase_currently_delivered_l3')

        if WeatherSettings.get_solo().track:
            data['temperature_x'] = [
                formats.date_format(
                    timezone.localtime(x.read_at), 'DSMR_GRAPH_SHORT_TIME_FORMAT'
                )
                for x in temperature
            ]
            data['temperature_y'] = [float(x.degrees_celcius) for x in temperature]

        return HttpResponse(json.dumps(data), content_type='application/json')

    def _parse_phases_data(self, data, field):
        return [
            float(getattr(x, field) * 1000)
            if getattr(x, field) else 0
            for x in data
        ]


@method_decorator(csrf_exempt, name='dispatch')
class DashboardXhrNotificationRead(FormView):
    """ XHR view for marking an in-app notification as read. """
    form_class = DashboardNotificationReadForm

    def form_valid(self, form):
        Notification.objects.filter(pk=form.cleaned_data['notification_id'], read=False).update(read=True)
        return HttpResponse(json.dumps({}), content_type='application/json')
