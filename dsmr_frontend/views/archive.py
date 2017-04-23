from collections import defaultdict
from datetime import time
import json

from dateutil.relativedelta import relativedelta
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse
from django.utils import timezone, formats
from django.utils.translation import ugettext as _

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_frontend.models.settings import FrontendSettings
from dsmr_stats.models.note import Note
import dsmr_backend.services
import dsmr_stats.services
from dsmr_frontend.templatetags.hex_to_rgb import hex_to_rgb


class Archive(TemplateView):
    template_name = 'dsmr_frontend/archive.html'

    def get_context_data(self, **kwargs):
        context_data = super(Archive, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['frontend_settings'] = FrontendSettings.get_solo()

        day_statistics = DayStatistics.objects.all().order_by('day')

        try:
            context_data['start_date'] = day_statistics[0].day
            context_data['end_date'] = day_statistics.order_by('-day')[0].day
        except IndexError:
            pass

        context_data['datepicker_locale_format'] = formats.get_format('DSMR_DATEPICKER_LOCALE_FORMAT')
        context_data['datepicker_date_format'] = 'DSMR_DATEPICKER_DATE_FORMAT'
        return context_data


class ArchiveXhrSummary(TemplateView):
    """ XHR view for fetching statistics, HTML response. """
    template_name = 'dsmr_frontend/fragments/archive-xhr-statistics.html'

    def get_context_data(self, **kwargs):
        context_data = super(ArchiveXhrSummary, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()
        context_data['frontend_settings'] = FrontendSettings.get_solo()

        selected_datetime = timezone.make_aware(timezone.datetime.strptime(
            self.request.GET['date'], formats.get_format('DSMR_STRFTIME_DATE_FORMAT')
        ))
        selected_level = self.request.GET['level']

        context_data['statistics'] = {
            'days': dsmr_stats.services.day_statistics(selected_datetime.date()),
            'months': dsmr_stats.services.month_statistics(selected_datetime.date()),
            'years': dsmr_stats.services.year_statistics(selected_datetime.date()),
        }[selected_level]

        context_data['title'] = {
            'days': formats.date_format(selected_datetime.date(), 'DSMR_GRAPH_LONG_DATE_FORMAT'),
            'months': formats.date_format(selected_datetime.date(), 'DSMR_DATEPICKER_MONTH'),
            'years': selected_datetime.date().year,
        }[selected_level]

        # Only day level allows some additional data.
        if selected_level == 'days':
            try:
                # This WILL fail when we either have no prices at all or conflicting ranges.
                context_data['energy_price'] = EnergySupplierPrice.objects.by_date(
                    target_date=selected_datetime.date()
                )
            except (EnergySupplierPrice.DoesNotExist, EnergySupplierPrice.MultipleObjectsReturned):
                # Default to zero prices.
                context_data['energy_price'] = EnergySupplierPrice()

            context_data['notes'] = Note.objects.filter(day=selected_datetime.date())

        context_data['selected_level'] = selected_level
        context_data['selected_datetime'] = selected_datetime
        context_data['django_date_format'] = 'DJANGO_DATE_FORMAT'
        return context_data


class ArchiveXhrGraphs(View):
    """ XHR view for fetching the hour statistics of a day, JSON encoded. """
    def get(self, request):  # noqa: C901
        capabilities = dsmr_backend.services.get_capabilities()
        frontend_settings = FrontendSettings.get_solo()
        selected_datetime = timezone.make_aware(timezone.datetime.strptime(
            self.request.GET['date'], formats.get_format('DSMR_STRFTIME_DATE_FORMAT')
        ))
        selected_level = self.request.GET['level']
        data = defaultdict(list)
        charts = {}
        x_format_callback = None
        FIELDS = (
            'electricity1', 'electricity2', 'electricity1_returned', 'electricity2_returned', 'electricity_merged',
            'electricity_returned_merged', 'gas'
        )

        # Zoom to hourly data.
        if selected_level == 'days':
            source_data = HourStatistics.objects.filter(
                hour_start__gte=selected_datetime,
                hour_start__lte=selected_datetime + timezone.timedelta(days=1)
            ).order_by('hour_start')
            x_format = 'DSMR_GRAPH_SHORT_TIME_FORMAT'
            x_axis = 'hour_start'
            x_format_callback = timezone.localtime

        # Zoom to daily data.
        elif selected_level == 'months':
            start_of_month = timezone.datetime(year=selected_datetime.year, month=selected_datetime.month, day=1)
            end_of_month = timezone.datetime.combine(start_of_month + relativedelta(months=1), time.min)
            source_data = DayStatistics.objects.filter(day__gte=start_of_month, day__lt=end_of_month).order_by('day')
            x_format = 'DSMR_GRAPH_SHORT_DATE_FORMAT'
            x_axis = 'day'

        # Zoom to monthly data.
        elif selected_level == 'years':
            source_data = []
            start_of_year = timezone.datetime(year=selected_datetime.year, month=1, day=1)

            for increment in range(0, 12):
                current_month = start_of_year + relativedelta(months=increment)
                current_month_stats = dsmr_stats.services.month_statistics(current_month.date())
                current_month_stats['month'] = current_month.date()
                source_data.append(current_month_stats)

            x_format = 'DSMR_DATEPICKER_MONTH'
            x_axis = 'month'

        for current_item in source_data:
            try:
                x_value = getattr(current_item, x_axis)
            except AttributeError:
                x_value = current_item[x_axis]

            if x_format_callback:
                x_value = x_format_callback(x_value)

            data['x'].append(formats.date_format(x_value, x_format))

            for current_field in FIELDS:
                try:
                    y_value = getattr(current_item, current_field) or 0
                except AttributeError:
                    y_value = current_item[current_field] or 0

                data[current_field].append(float(y_value))

        if frontend_settings.merge_electricity_tariffs:
            charts['electricity'] = {
                'labels': data['x'],
                'datasets': [{
                    'data': data['electricity_merged'],
                    'label': _('Electricity (single tariff)'),
                    'backgroundColor': "rgba({},0.1)".format(hex_to_rgb(frontend_settings.electricity_delivered_color)),
                    'borderColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.electricity_delivered_color)),
                    'pointColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.electricity_delivered_color)),
                    'pointStrokeColor': "#fff",
                    'pointHoverBackgroundColor': "#fff",
                }]
            }
        else:
            charts['electricity'] = {
                'labels': data['x'],
                'datasets': [{
                    'data': data['electricity1'],
                    'label': _('Electricity 1 (low tariff)'),
                    'backgroundColor': "rgba({},0.1)".format(hex_to_rgb(
                        frontend_settings.electricity_delivered_alternate_color
                    )),
                    'borderColor': "rgba({},1)".format(hex_to_rgb(
                        frontend_settings.electricity_delivered_alternate_color
                    )),
                    'pointColor': "rgba({},1)".format(hex_to_rgb(
                        frontend_settings.electricity_delivered_alternate_color
                    )),
                    'pointStrokeColor': "#fff",
                    'pointHoverBackgroundColor': "#fff",
                }, {
                    'data': data['electricity2'],
                    'label': _('Electricity 2 (high tariff)'),
                    'backgroundColor': "rgba({},0.1)".format(hex_to_rgb(frontend_settings.electricity_delivered_color)),
                    'borderColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.electricity_delivered_color)),
                    'pointColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.electricity_delivered_color)),
                    'pointStrokeColor': "#fff",
                    'pointHoverBackgroundColor': "#fff",
                }]
            }

        if capabilities['electricity_returned']:
            if frontend_settings.merge_electricity_tariffs:
                charts['electricity_returned'] = {
                    'labels': data['x'],
                    'datasets': [{
                        'data': data['electricity_returned_merged'],
                        'label': _('Electricity returned (single tariff)'),
                        'backgroundColor': "rgba({},0.1)".format(hex_to_rgb(
                            frontend_settings.electricity_returned_color
                        )),
                        'borderColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.electricity_returned_color)),
                        'pointColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.electricity_returned_color)),
                        'pointStrokeColor': "#fff",
                        'pointHoverBackgroundColor': "#fff",
                    }]
                }
            else:
                charts['electricity_returned'] = {
                    'labels': data['x'],
                    'datasets': [{
                        'data': data['electricity1_returned'],
                        'label': _('Electricity 1 returned (low tariff)'),
                        'backgroundColor': "rgba({},0.1)".format(hex_to_rgb(
                            frontend_settings.electricity_returned_alternate_color
                        )),
                        'borderColor': "rgba({},1)".format(hex_to_rgb(
                            frontend_settings.electricity_returned_alternate_color
                        )),
                        'pointColor': "rgba({},1)".format(hex_to_rgb(
                            frontend_settings.electricity_returned_alternate_color
                        )),
                        'pointStrokeColor': "#fff",
                        'pointHoverBackgroundColor': "#fff",
                    }, {
                        'data': data['electricity2_returned'],
                        'label': _('Electricity 2 returned (high tariff)'),
                        'backgroundColor': "rgba({},0.1)".format(hex_to_rgb(
                            frontend_settings.electricity_returned_color
                        )),
                        'borderColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.electricity_returned_color)),
                        'pointColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.electricity_returned_color)),
                        'pointStrokeColor': "#fff",
                        'pointHoverBackgroundColor': "#fff",
                    }]
                }

        if capabilities['gas']:
            charts['gas'] = {
                'labels': data['x'],
                'datasets': [{
                    'data': data['gas'],
                    'label': _('Gas'),
                    'backgroundColor': "rgba({},0.1)".format(hex_to_rgb(frontend_settings.gas_delivered_color)),
                    'borderColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.gas_delivered_color)),
                    'pointColor': "rgba({},1)".format(hex_to_rgb(frontend_settings.gas_delivered_color)),
                    'pointStrokeColor': "#fff",
                    'pointHoverBackgroundColor': "#fff",
                }]
            }

        return HttpResponse(
            json.dumps({
                'charts': charts,
            }),
            content_type='application/json'
        )
