from django.views.generic.base import TemplateView, View
from django.utils import formats, timezone
from django.http import JsonResponse

from dsmr_stats.models.statistics import DayStatistics, HourStatistics


class Archive(TemplateView):
    template_name = 'dsmr_frontend/archive.html'

    def get_context_data(self, **kwargs):
        context_data = super(Archive, self).get_context_data(**kwargs)
        day_statistics = DayStatistics.objects.all().order_by('pk')
        context_data['start_date'] = day_statistics[0].day
        context_data['end_date'] = day_statistics.order_by('-pk')[0].day
        context_data['datepicker_locale_format'] = formats.get_format('DSMR_DATEPICKER_LOCALE_FORMAT')
        context_data['datepicker_date_format'] = 'DSMR_DATEPICKER_DATE_FORMAT'

        return context_data


class ArchiveXhr(View):
    """ XHR view for fetching day data. """

    def get(self, request):
        selected_datetime = timezone.make_aware(timezone.datetime.strptime(
            self.request.GET['date'], formats.get_format('DSMR_STRFTIME_DATE_FORMAT')
        ))

        data = {}
        data['day_statistics'] = DayStatistics.objects.filter(
            day=selected_datetime.date()
        ).values_list()
        data['hour_statistics'] = HourStatistics.objects.filter(
            hour_start__gte=selected_datetime,
            hour_start__lt=selected_datetime + timezone.timedelta(days=1)
        ).values_list()

        return JsonResponse(data)
