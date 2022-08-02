from django_filters import rest_framework as filters

from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_consumption.models.consumption import GasConsumption, ElectricityConsumption
from dsmr_stats.models.statistics import DayStatistics, HourStatistics


class DsmrReadingFilter(filters.FilterSet):
    FIELD = "timestamp"
    timestamp__gte = filters.DateTimeFilter(
        field_name=FIELD,
        lookup_expr="gte",
        label="Reading timestamp must be after or equal to `X`",
    )
    timestamp__lte = filters.DateTimeFilter(
        field_name=FIELD,
        lookup_expr="lte",
        label="Reading timestamp must be before or equal to `X`",
    )

    class Meta:
        model = DsmrReading
        fields = [
            "timestamp"
        ]  # Deprecated. Revert to empty list in some major API bump.


class EnergySupplierPriceFilter(filters.FilterSet):
    start__gte = filters.DateFilter(
        field_name="start",
        lookup_expr="gte",
        label="Contract start date must be after or equal to `X`",
    )
    start__lte = filters.DateFilter(
        field_name="start",
        lookup_expr="lte",
        label="Contract start date must be before or equal to `X`",
    )
    end__gte = filters.DateFilter(
        field_name="end",
        lookup_expr="gte",
        label="Contract end date must be after or equal to `X`",
    )
    end__lte = filters.DateFilter(
        field_name="end",
        lookup_expr="lte",
        label="Contract end date must be before or equal to `X`",
    )

    class Meta:
        model = EnergySupplierPrice
        fields = []


class ElectricityConsumptionFilter(filters.FilterSet):
    FIELD = "read_at"
    read_at__gte = filters.DateTimeFilter(
        field_name=FIELD,
        lookup_expr="gte",
        label="Consumption timestamp must be after or equal to `X`",
    )
    read_at__lte = filters.DateTimeFilter(
        field_name=FIELD,
        lookup_expr="lte",
        label="Consumption timestamp must be before or equal to `X`",
    )

    class Meta:
        model = ElectricityConsumption
        fields = ["read_at"]  # Deprecated. Revert to empty list in some major API bump.


class GasConsumptionFilter(filters.FilterSet):
    FIELD = "read_at"
    read_at__gte = filters.DateTimeFilter(
        field_name=FIELD,
        lookup_expr="gte",
        label="Consumption timestamp must be after or equal to `X`",
    )
    read_at__lte = filters.DateTimeFilter(
        field_name=FIELD,
        lookup_expr="lte",
        label="Consumption timestamp must be before or equal to `X`",
    )

    class Meta:
        model = GasConsumption
        fields = ["read_at"]  # Deprecated. Revert to empty list in some major API bump.


class DayStatisticsFilter(filters.FilterSet):
    FIELD = "day"
    day__gte = filters.DateFilter(
        field_name=FIELD, lookup_expr="gte", label="Date must be after or equal to `X`"
    )
    day__lte = filters.DateFilter(
        field_name=FIELD, lookup_expr="lte", label="Date must be before or equal to `X`"
    )

    class Meta:
        model = DayStatistics
        fields = ["day"]  # Deprecated. Revert to empty list in some major API bump.


class HourStatisticsFilter(filters.FilterSet):
    FIELD = "hour_start"
    hour_start__gte = filters.DateTimeFilter(
        field_name=FIELD,
        lookup_expr="gte",
        label="Hour start must be after or equal to `X`",
    )
    hour_start__lte = filters.DateTimeFilter(
        field_name=FIELD,
        lookup_expr="lte",
        label="Hour start must be before or equal to `X`",
    )

    class Meta:
        model = HourStatistics
        fields = [
            "hour_start"
        ]  # Deprecated. Revert to empty list in some major API bump.
