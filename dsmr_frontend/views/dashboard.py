import json

from django.views.generic.base import TemplateView, View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.utils import formats, timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_frontend.forms import DashboardNotificationReadForm, DashboardElectricityConsumptionForm
from dsmr_weather.models.reading import TemperatureReading
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_frontend.models.message import Notification
from dsmr_datalogger.models.settings import DataloggerSettings
import dsmr_consumption.services
import dsmr_backend.services.backend
import dsmr_stats.services


XHR_RECENT_CONSUMPTION_HOURS_AGO = 24


class Dashboard(TemplateView):
    template_name = 'dsmr_frontend/dashboard.html'

    def get_context_data(self, **kwargs):
        context_data = super(Dashboard, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.backend.get_capabilities()
        context_data['datalogger_settings'] = DataloggerSettings.get_solo()
        context_data['frontend_settings'] = FrontendSettings.get_solo()
        context_data['notifications'] = Notification.objects.unread()

        today = timezone.localtime(timezone.now()).date()
        context_data['month_statistics'] = dsmr_stats.services.month_statistics(target_date=today)
        return context_data


class DashboardXhrHeader(View):
    """ XHR view for fetching the dashboard header, displaying latest readings and price estimate, JSON response. """
    def get(self, request):
        return HttpResponse(
            json.dumps(dsmr_consumption.services.live_electricity_consumption(use_naturaltime=True)),
            content_type='application/json'
        )


class DashboardXhrConsumption(TemplateView):
    """ XHR view for fetching consumption, HTML response. """
    template_name = 'dsmr_frontend/fragments/dashboard-xhr-consumption.html'

    def get_context_data(self, **kwargs):
        context_data = super(DashboardXhrConsumption, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.backend.get_capabilities()
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


class DashboardXhrElectricityConsumption(View):
    """ XHR view for fetching the electricity consumption graph data, in JSON. """
    def get(self, request):  # noqa: C901
        form = DashboardElectricityConsumptionForm(request.GET)

        if not form.is_valid():
            return HttpResponseBadRequest(
                json.dumps({'errors': form.errors}),
                content_type='application/json'
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
        }

        # Optional delta.
        latest_delta_id = form.cleaned_data.get('latest_delta_id')

        # Optimize queries for large datasets by restricting the data to the last week in the first place.
        base_timestamp = timezone.now() - timezone.timedelta(hours=XHR_RECENT_CONSUMPTION_HOURS_AGO)
        electricity = ElectricityConsumption.objects.filter(read_at__gt=base_timestamp).order_by('read_at')

        if latest_delta_id:
            electricity = electricity.filter(id__gt=latest_delta_id)

        for current in electricity:
            read_at = formats.date_format(timezone.localtime(current.read_at), 'DSMR_GRAPH_LONG_TIME_FORMAT')

            data['read_at'].append(read_at)

            if form.cleaned_data.get('delivered'):
                data['currently_delivered'].append(float(current.currently_delivered) * 1000)

            if form.cleaned_data.get('returned'):
                data['currently_returned'].append(float(current.currently_returned) * 1000)

            if form.cleaned_data.get('phases'):
                # 'or 0' is required due to empty data.
                data['phases_delivered']['l1'].append(float(current.phase_currently_delivered_l1 or 0) * 1000)
                data['phases_delivered']['l2'].append(float(current.phase_currently_delivered_l2 or 0) * 1000)
                data['phases_delivered']['l3'].append(float(current.phase_currently_delivered_l3 or 0) * 1000)

                if form.cleaned_data.get('returned'):
                    # 'or 0' is required due to backwards compatibility.
                    data['phases_returned']['l1'].append(float(current.phase_currently_returned_l1 or 0) * 1000)
                    data['phases_returned']['l2'].append(float(current.phase_currently_returned_l2 or 0) * 1000)
                    data['phases_returned']['l3'].append(float(current.phase_currently_returned_l3 or 0) * 1000)

            data['latest_delta_id'] = current.id

        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )


class DashboardXhrGasConsumption(View):
    """ XHR view for fetching the gas consumption graph data, in JSON. """
    def get(self, request):  # noqa: C901
        data = {
            'read_at': [],
            'currently_delivered': [],
        }

        # Optimize queries for large datasets by restricting the data to the last week in the first place.
        base_timestamp = timezone.now() - timezone.timedelta(hours=XHR_RECENT_CONSUMPTION_HOURS_AGO)
        gas = GasConsumption.objects.filter(read_at__gt=base_timestamp).order_by('read_at')

        for current in gas:
            read_at = formats.date_format(timezone.localtime(current.read_at), 'DSMR_GRAPH_LONG_TIME_FORMAT')
            data['read_at'].append(read_at)
            data['currently_delivered'].append(float(current.currently_delivered))

        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )


class DashboardXhrTemperature(View):
    """ XHR view for fetching the temperature graph data, in JSON. """
    def get(self, request):  # noqa: C901
        data = {
            'read_at': [],
            'degrees_celcius': [],
        }

        # Optimize queries for large datasets by restricting the data to the last week in the first place.
        base_timestamp = timezone.now() - timezone.timedelta(hours=XHR_RECENT_CONSUMPTION_HOURS_AGO)
        temperature = TemperatureReading.objects.filter(read_at__gt=base_timestamp).order_by('read_at')

        for current in temperature:
            read_at = formats.date_format(timezone.localtime(current.read_at), 'DSMR_GRAPH_LONG_TIME_FORMAT')
            data['read_at'].append(read_at)
            data['degrees_celcius'].append(float(current.degrees_celcius))

        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )


@method_decorator(csrf_exempt, name='dispatch')
class DashboardXhrNotificationRead(FormView):
    """ XHR view for marking an in-app notification as read. """
    form_class = DashboardNotificationReadForm

    def form_valid(self, form):
        Notification.objects.filter(pk=form.cleaned_data['notification_id'], read=False).update(read=True)
        return HttpResponse(json.dumps({}), content_type='application/json')
