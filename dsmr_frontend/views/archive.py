from collections import defaultdict
import json

from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse
from django.utils import formats, timezone

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_consumption.models.energysupplier import EnergySupplierPrice


class Archive(TemplateView):
    template_name = 'dsmr_frontend/archive.html'

    def get_context_data(self, **kwargs):
        context_data = super(Archive, self).get_context_data(**kwargs)
        day_statistics = DayStatistics.objects.all().order_by('pk')

        try:
            context_data['start_date'] = day_statistics[0].day
            context_data['end_date'] = day_statistics.order_by('-pk')[0].day
        except IndexError:
            pass

        context_data['datepicker_locale_format'] = formats.get_format('DSMR_DATEPICKER_LOCALE_FORMAT')
        context_data['datepicker_date_format'] = 'DSMR_DATEPICKER_DATE_FORMAT'
        return context_data


class ArchiveXhrDayStatistics(TemplateView):
    """ XHR view for fetching day statistics, HTML response. """
    template_name = 'dsmr_frontend/fragments/archive.html'

    def get_context_data(self, **kwargs):
        context_data = super(ArchiveXhrDayStatistics, self).get_context_data(**kwargs)
        selected_datetime = timezone.make_aware(timezone.datetime.strptime(
            self.request.GET['date'], formats.get_format('DSMR_STRFTIME_DATE_FORMAT')
        ))
        context_data['statistics'] = DayStatistics.objects.get(
            day=selected_datetime.date()
        )

        try:
            # This WILL fail when we either have no prices at all or conflicting ranges.
            context_data['energy_price'] = EnergySupplierPrice.objects.by_date(
                target_date=selected_datetime.date()
            )
        except (EnergySupplierPrice.DoesNotExist, EnergySupplierPrice.MultipleObjectsReturned):
            # Default to zero prices.
            context_data['energy_price'] = EnergySupplierPrice()

        return context_data


class ArchiveXhrHourStatistics(View):
    """ XHR view for fetching the hour statistics of a day, JSON encoded. """
    def get(self, request):
        selected_datetime = timezone.make_aware(timezone.datetime.strptime(
            self.request.GET['date'], formats.get_format('DSMR_STRFTIME_DATE_FORMAT')
        ))

        hour_statistics = HourStatistics.objects.filter(
            hour_start__gte=selected_datetime,
            hour_start__lt=selected_datetime + timezone.timedelta(days=1)
        ).order_by('hour_start')

        data = defaultdict(list)
        FIELDS = (
            'electricity1', 'electricity2', 'electricity1_returned', 'electricity2_returned', 'gas'
        )

        for current_hour in hour_statistics:
            data['x'].append(formats.date_format(
                timezone.localtime(current_hour.hour_start), 'DSMR_GRAPH_SHORT_DATETIME_FORMAT'
            ))

            for current_field in FIELDS:
                value = getattr(current_hour, current_field) or 0
                data[current_field].append(float(value))

        return HttpResponse(
            json.dumps(data),
            content_type='application/json'
        )
