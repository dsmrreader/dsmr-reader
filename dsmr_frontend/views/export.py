import datetime
import csv

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import StreamingHttpResponse
from django.views.generic.base import TemplateView
from django.views.generic.edit import BaseFormView
from django.urls import reverse
from django.utils import timezone, formats
from django.shortcuts import redirect

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_frontend.forms import ExportAsCsvForm
import dsmr_backend.services
from decimal import Decimal


class Export(LoginRequiredMixin, TemplateView):
    template_name = 'dsmr_frontend/export.html'

    def get_context_data(self, **kwargs):
        context_data = super(Export, self).get_context_data(**kwargs)
        context_data['capabilities'] = dsmr_backend.services.get_capabilities()

        day_statistics = DayStatistics.objects.all().order_by('pk')

        try:
            context_data['start_date'] = day_statistics[0].day
            context_data['end_date'] = day_statistics.order_by('-pk')[0].day
        except IndexError:
            context_data['start_date'] = None
            context_data['end_date'] = None

        context_data['datepicker_locale_format'] = formats.get_format('DSMR_DATEPICKER_LOCALE_FORMAT')
        context_data['datepicker_date_format'] = 'DSMR_DATEPICKER_DATE_FORMAT'
        return context_data


class ExportAsCsv(LoginRequiredMixin, BaseFormView):
    """ Exports the selected data in CSV format. """
    form_class = ExportAsCsvForm

    def form_invalid(self, form):
        return redirect(reverse('frontend:export'))

    def form_valid(self, form):
        start_date = form.cleaned_data['start_date']
        start_date = timezone.localtime(timezone.make_aware(timezone.datetime(
            start_date.year, start_date.month, start_date.day
        )))
        end_date = form.cleaned_data['end_date']
        end_date = timezone.localtime(timezone.make_aware(timezone.datetime(
            end_date.year, end_date.month, end_date.day
        )))
        data_type = form.cleaned_data['data_type']

        if data_type == ExportAsCsvForm.DATA_TYPE_DAY:
            source_data = DayStatistics.objects.filter(
                day__gte=start_date.date(), day__lte=end_date.date()
            ).order_by('day')
            export_fields = [
                'day', 'electricity1', 'electricity2', 'electricity1_returned',
                'electricity2_returned', 'gas', 'electricity1_cost', 'electricity2_cost',
                'gas_cost', 'total_cost'
            ]

        else:  # if data_type == ExportAsCsvForm.DATA_TYPE_HOUR:
            source_data = HourStatistics.objects.filter(
                hour_start__gte=start_date, hour_start__lte=end_date
            ).order_by('hour_start')
            export_fields = [
                'hour_start', 'electricity1', 'electricity2', 'electricity1_returned',
                'electricity2_returned', 'gas'
            ]

        # Direct copy from Django docs.
        class Echo(object):
            """ An object that implements just the write method of the file-like interface. """
            def write(self, value):
                """ Write the value by returning it, instead of storing in a buffer. """
                return value

        pseudo_buffer = Echo()
        writer = csv.writer(pseudo_buffer)
        response = StreamingHttpResponse(
            (
                self._generate_csv_row(writer, source_data, export_fields)
            ),
            content_type='text/csv'
        )
        attachment_name = 'dsmrreader-data-export---{}__{}__{}.csv'.format(
            data_type, start_date.date(), end_date.date()
        )
        response['Content-Disposition'] = 'attachment; filename="{}"'.format(attachment_name)
        return response

    def _generate_csv_row(self, writer, data, fields):
        if not data:
            raise StopIteration()

        # Write header, but use the fields' verbose name.
        data_class = data[0].__class__
        header = [data_class._meta.get_field(x).verbose_name.title() for x in fields]

        yield writer.writerow(header)

        for current_data in data:
            yield writer.writerow([
                self._serialize_field(
                    getattr(current_data, current_field)
                ) for current_field in fields
            ])

        raise StopIteration()

    def _serialize_field(self, data):
        if isinstance(data, Decimal):
            return float(data)

        elif isinstance(data, datetime.datetime):
            return formats.date_format(data, 'DSMR_EXPORT_DATETIME_FORMAT')

        elif isinstance(data, datetime.date):  # pragma: no cover
            return formats.date_format(data, 'DSMR_DATEPICKER_DATE_FORMAT')
