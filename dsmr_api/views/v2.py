from rest_framework import mixins, viewsets

from dsmr_consumption.serializers.consumption import ElectricityConsumptionSerializer, GasConsumptionSerializer
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_stats.serializers.statistics import DayStatisticsSerializer, HourStatisticsSerializer
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_datalogger.serializers.reading import DsmrReadingSerializer
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_api.filters import DsmrReadingFilter, DayStatisticsFilter, ElectricityConsumptionFilter,\
    GasConsumptionFilter, HourStatisticsFilter


class DsmrReadingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    FIELD = 'timestamp'
    queryset = DsmrReading.objects.all()
    serializer_class = DsmrReadingSerializer
    filter_class = DsmrReadingFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


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
