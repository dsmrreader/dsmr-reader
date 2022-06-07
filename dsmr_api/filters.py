from django_filters import rest_framework as filters

from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import GasConsumption, ElectricityConsumption
from dsmr_stats.models.statistics import DayStatistics, HourStatistics


class DsmrReadingFilter(filters.FilterSet):
    FIELD = 'timestamp'
    timestamp__gte = filters.DateTimeFilter(field_name=FIELD, lookup_expr='gte')
    timestamp__lte = filters.DateTimeFilter(field_name=FIELD, lookup_expr='lte')

    class Meta:
        model = DsmrReading
        fields = ['timestamp']


class EnergySupplierPriceFilter(filters.FilterSet):
    start__gte = filters.DateFilter(field_name='start', lookup_expr='gte', label='Contract start date must be >= `X`')
    start__lte = filters.DateFilter(field_name='start', lookup_expr='lte', label='Contract start date must be <= `X`')
    end__gte = filters.DateFilter(field_name='end', lookup_expr='gte', label='Contract end date must be  >= `X`')
    end__lte = filters.DateFilter(field_name='end', lookup_expr='lte', label='Contract end date must be  <= `X`')

    class Meta:
        model = EnergySupplierPrice
        fields = []


class ElectricityConsumptionFilter(filters.FilterSet):
    FIELD = 'read_at'
    read_at__gte = filters.DateTimeFilter(field_name=FIELD, lookup_expr='gte')
    read_at__lte = filters.DateTimeFilter(field_name=FIELD, lookup_expr='lte')

    class Meta:
        model = ElectricityConsumption
        fields = ['read_at']


class GasConsumptionFilter(filters.FilterSet):
    FIELD = 'read_at'
    read_at__gte = filters.DateTimeFilter(field_name=FIELD, lookup_expr='gte')
    read_at__lte = filters.DateTimeFilter(field_name=FIELD, lookup_expr='lte')

    class Meta:
        model = GasConsumption
        fields = ['read_at']


class DayStatisticsFilter(filters.FilterSet):
    FIELD = 'day'
    day__gte = filters.DateFilter(field_name=FIELD, lookup_expr='gte')
    day__lte = filters.DateFilter(field_name=FIELD, lookup_expr='lte')

    class Meta:
        model = DayStatistics
        fields = ['day']


class HourStatisticsFilter(filters.FilterSet):
    FIELD = 'hour_start'
    hour_start__gte = filters.DateTimeFilter(field_name=FIELD, lookup_expr='gte')
    hour_start__lte = filters.DateTimeFilter(field_name=FIELD, lookup_expr='lte')

    class Meta:
        model = HourStatistics
        fields = ['hour_start']
