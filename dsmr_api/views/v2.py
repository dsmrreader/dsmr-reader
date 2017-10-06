from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from dsmr_consumption.serializers.consumption import ElectricityConsumptionSerializer, GasConsumptionSerializer
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.serializers.statistics import DayStatisticsSerializer, HourStatisticsSerializer
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_datalogger.serializers.reading import DsmrReadingSerializer
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_api.filters import DsmrReadingFilter, DayStatisticsFilter, ElectricityConsumptionFilter,\
    GasConsumptionFilter, HourStatisticsFilter
import dsmr_consumption.services


class DsmrReadingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    FIELD = 'timestamp'
    queryset = DsmrReading.objects.all()
    serializer_class = DsmrReadingSerializer
    filter_class = DsmrReadingFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class TodayConsumptionView(APIView):
    """ Returns the consumption (so far) of the current day. """
    IGNORE_FIELDS = (
        'electricity1_start', 'electricity2_start', 'electricity1_end', 'electricity2_end', 'notes', 'gas_start',
        'gas_end', 'electricity1_returned_start', 'electricity2_returned_start', 'electricity1_returned_end',
        'electricity2_returned_end', 'electricity_cost_merged', 'electricity_merged', 'electricity_returned_merged',
        'average_temperature', 'lowest_temperature', 'highest_temperature', 'latest_consumption'
    )

    def get(self, request):
        try:
            day_totals = dsmr_consumption.services.day_consumption(
                day=timezone.localtime(timezone.now()).date()
            )
        except LookupError as error:
            return Response(str(error))

        # Some fields are only for internal use.
        for x in self.IGNORE_FIELDS:
            if x in day_totals.keys():
                del day_totals[x]

        return Response(day_totals)


class ElectricityConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    FIELD = 'read_at'
    queryset = ElectricityConsumption.objects.all()
    serializer_class = ElectricityConsumptionSerializer
    filter_class = ElectricityConsumptionFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class GasConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    FIELD = 'read_at'
    queryset = GasConsumption.objects.all()
    serializer_class = GasConsumptionSerializer
    filter_class = GasConsumptionFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class DayStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    FIELD = 'day'
    queryset = DayStatistics.objects.all()
    serializer_class = DayStatisticsSerializer
    filter_class = DayStatisticsFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class HourStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    FIELD = 'hour_start'
    queryset = HourStatistics.objects.all()
    serializer_class = HourStatisticsSerializer
    filter_class = HourStatisticsFilter
    ordering_fields = (FIELD, )
    ordering = FIELD
