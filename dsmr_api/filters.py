from django_filters import rest_framework as filters

from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import GasConsumption, ElectricityConsumption
from dsmr_stats.models.statistics import DayStatistics, HourStatistics


class DsmrReadingFilter(filters.FilterSet):
    FIELD = 'timestamp'
    timestamp__gte = filters.DateTimeFilter(name=FIELD, lookup_expr='gte')
    timestamp__lte = filters.DateTimeFilter(name=FIELD, lookup_expr='lte')

    class Meta:
        model = DsmrReading
        fields = ['timestamp']


class ElectricityConsumptionFilter(filters.FilterSet):
    FIELD = 'read_at'
    read_at__gte = filters.DateTimeFilter(name=FIELD, lookup_expr='gte')
    read_at__lte = filters.DateTimeFilter(name=FIELD, lookup_expr='lte')

    class Meta:
        model = ElectricityConsumption
        fields = ['read_at']


class GasConsumptionFilter(filters.FilterSet):
    FIELD = 'read_at'
    read_at__gte = filters.DateTimeFilter(name=FIELD, lookup_expr='gte')
    read_at__lte = filters.DateTimeFilter(name=FIELD, lookup_expr='lte')

    class Meta:
        model = GasConsumption
        fields = ['read_at']


class DayStatisticsFilter(filters.FilterSet):
    FIELD = 'day'
    day__gte = filters.DateFilter(name=FIELD, lookup_expr='gte')
    day__lte = filters.DateFilter(name=FIELD, lookup_expr='lte')

    class Meta:
        model = DayStatistics
        fields = ['day']


class HourStatisticsFilter(filters.FilterSet):
    FIELD = 'hour_start'
    hour_start__gte = filters.DateTimeFilter(name=FIELD, lookup_expr='gte')
    hour_start__lte = filters.DateTimeFilter(name=FIELD, lookup_expr='lte')

    class Meta:
        model = HourStatistics
        fields = ['hour_start']
