import json

from django.http import JsonResponse
from django.views.generic.base import TemplateView, View
from django.utils import formats, timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_frontend.forms import DashboardElectricityConsumptionForm
from dsmr_frontend.mixins import ConfigurableLoginRequiredMixin
from dsmr_weather.models.reading import TemperatureReading
from dsmr_frontend.models.settings import FrontendSettings, SortedGraph
from dsmr_frontend.models.message import Notification
from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_backend.services.backend
import dsmr_stats.services


class LiveGraphs(ConfigurableLoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/live-graphs.html'

    def get_context_data(self, **kwargs):
        context_data = super(LiveGraphs, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.backend.get_capabilities()
        context_data['datalogger_settings'] = DataloggerSettings.get_solo()
        context_data['frontend_settings'] = FrontendSettings.get_solo()
        context_data['notification_count'] = Notification.objects.unread().count()
        context_data['sorted_graphs_json'] = json.dumps(list(
            SortedGraph.objects.all().values_list('graph_type', flat=True)
        ))

        today = timezone.localtime(timezone.now()).date()
        context_data['month_statistics'] = dsmr_stats.services.month_statistics(target_date=today)
        return context_data


class LiveXhrElectricityConsumption(ConfigurableLoginRequiredMixin, View):
    """ XHR view for fetching the electricity consumption graph data, in JSON. """
    def get(self, request):  # noqa: C901
        form = DashboardElectricityConsumptionForm(request.GET)

        if not form.is_valid():
            return JsonResponse({
                    'errors': form.errors
                },
                status=400
            )

        data = {
            'latest_delta_id': 0,
            'read_at': [],
            'currently_delivered': [],
            'currently_returned': [],
            'phases_delivered': {
                'l1': [],
                'l2': [],
                'l3': [],
            },
            'phases_returned': {
                'l1': [],
                'l2': [],
                'l3': [],
            },
            'phase_voltage': {
                'l1': [],
                'l2': [],
                'l3': [],
            },
            'phase_power_current': {
                'l1': [],
                'l2': [],
                'l3': [],
            },
        }

        # Optional delta.
        latest_delta_id = form.cleaned_data.get('latest_delta_id')

        # Optimize queries for large datasets by restricting the data (when using the installation default).
        base_timestamp = timezone.now() - timezone.timedelta(
            hours=FrontendSettings.get_solo().live_graphs_hours_range
        )
        electricity = ElectricityConsumption.objects.filter(read_at__gt=base_timestamp).order_by('read_at')

        if latest_delta_id:
            electricity = electricity.filter(id__gt=latest_delta_id)

        for current in electricity:
            read_at = formats.date_format(timezone.localtime(current.read_at), 'DSMR_GRAPH_LONG_TIME_FORMAT')

            data['read_at'].append(read_at)

            if form.cleaned_data.get('delivered'):
                data['currently_delivered'].append(self._convert_to_watt(current.currently_delivered))

            if form.cleaned_data.get('returned'):
                data['currently_returned'].append(self._convert_to_watt(current.currently_returned))

            if form.cleaned_data.get('phases'):
                # 'or 0' is required due to empty data.
                data['phases_delivered']['l1'].append(self._convert_to_watt(current.phase_currently_delivered_l1))
                data['phases_delivered']['l2'].append(self._convert_to_watt(current.phase_currently_delivered_l2))
                data['phases_delivered']['l3'].append(self._convert_to_watt(current.phase_currently_delivered_l3))

                if form.cleaned_data.get('returned'):
                    # 'or 0' is required due to backwards compatibility.
                    data['phases_returned']['l1'].append(self._convert_to_watt(current.phase_currently_returned_l1))
                    data['phases_returned']['l2'].append(self._convert_to_watt(current.phase_currently_returned_l2))
                    data['phases_returned']['l3'].append(self._convert_to_watt(current.phase_currently_returned_l3))

            if form.cleaned_data.get('voltage'):
                data['phase_voltage']['l1'].append(float(current.phase_voltage_l1 or 0))
                data['phase_voltage']['l2'].append(float(current.phase_voltage_l2 or 0))
                data['phase_voltage']['l3'].append(float(current.phase_voltage_l3 or 0))

            if form.cleaned_data.get('power_current'):
                data['phase_power_current']['l1'].append(current.phase_power_current_l1 or 0)
                data['phase_power_current']['l2'].append(current.phase_power_current_l2 or 0)
                data['phase_power_current']['l3'].append(current.phase_power_current_l3 or 0)

            data['latest_delta_id'] = current.id

        return JsonResponse(data)

    def _convert_to_watt(self, kw_or_none):
        if kw_or_none is None:
            return 0

        return int(kw_or_none * 1000)


class LiveXhrGasConsumption(ConfigurableLoginRequiredMixin, View):
    """ XHR view for fetching the gas consumption graph data, in JSON. """
    def get(self, request):  # noqa: C901
        data = {
            'read_at': [],
            'currently_delivered': [],
        }

        # Optimize queries for large datasets by restricting the data to the last week in the first place.
        base_timestamp = timezone.now() - timezone.timedelta(
            hours=FrontendSettings.get_solo().live_graphs_hours_range
        )
        gas = GasConsumption.objects.filter(read_at__gt=base_timestamp).order_by('read_at')

        for current in gas:
            read_at = formats.date_format(timezone.localtime(current.read_at), 'DSMR_GRAPH_LONG_TIME_FORMAT')
            data['read_at'].append(read_at)
            data['currently_delivered'].append(float(current.currently_delivered))

        return JsonResponse(data)


class LiveXhrTemperature(ConfigurableLoginRequiredMixin, View):
    """ XHR view for fetching the temperature graph data, in JSON. """
    def get(self, request):  # noqa: C901
        data = {
            'read_at': [],
            'degrees_celcius': [],
        }

        # Optimize queries for large datasets by restricting the data to the last week in the first place.
        base_timestamp = timezone.now() - timezone.timedelta(
            hours=FrontendSettings.get_solo().live_graphs_hours_range
        )
        temperature = TemperatureReading.objects.filter(read_at__gt=base_timestamp).order_by('read_at')

        for current in temperature:
            read_at = formats.date_format(timezone.localtime(current.read_at), 'DSMR_GRAPH_LONG_TIME_FORMAT')
            data['read_at'].append(read_at)
            data['degrees_celcius'].append(float(current.degrees_celcius))

        return JsonResponse(data)
