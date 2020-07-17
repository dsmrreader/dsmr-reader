from decimal import Decimal

from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.conf import settings

from dsmr_consumption.serializers.consumption import ElectricityConsumptionSerializer, GasConsumptionSerializer
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.serializers.statistics import MeterStatisticsSerializer
from dsmr_stats.serializers.statistics import DayStatisticsSerializer, HourStatisticsSerializer
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_datalogger.serializers.reading import DsmrReadingSerializer
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_api.filters import DsmrReadingFilter, DayStatisticsFilter, ElectricityConsumptionFilter,\
    GasConsumptionFilter, HourStatisticsFilter
import dsmr_consumption.services
import dsmr_datalogger.signals


class DsmrReadingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
    Returns a list of DSMR-readings.

    create:
    Creates a new DSMR-reading.
    """
    FIELD = 'timestamp'
    queryset = DsmrReading.objects.all()
    serializer_class = DsmrReadingSerializer
    filterset_class = DsmrReadingFilter
    ordering_fields = (FIELD, )
    ordering = FIELD

    def perform_create(self, serializer):
        """ Overrided to support custom model creation signal."""
        new_instance = serializer.save()
        dsmr_datalogger.signals.dsmr_reading_created.send_robust(None, instance=new_instance)


class MeterStatisticsViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """ Retrieves en updates meter statistics. """
    serializer_class = MeterStatisticsSerializer

    def get_object(self):
        # This is a REALLY good combo with django-solo, as it fits perfectly for a singleton retreiver and updater!
        return MeterStatistics.get_solo()


class TodayConsumptionView(APIView):
    """ Returns the consumption of the current day (so far). """
    IGNORE_FIELDS = (
        'electricity1_start', 'electricity2_start', 'electricity1_end', 'electricity2_end', 'notes', 'gas_start',
        'gas_end', 'electricity1_returned_start', 'electricity2_returned_start', 'electricity1_returned_end',
        'electricity2_returned_end', 'electricity_cost_merged',
        'average_temperature', 'lowest_temperature', 'highest_temperature', 'latest_consumption'
    )
    DEFAULT_ZERO_FIELDS = ('gas', 'gas_cost')  # These might miss during the first hour of each day.

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

        # Default these, if omitted.
        for x in self.DEFAULT_ZERO_FIELDS:
            if x not in day_totals.keys():
                day_totals[x] = Decimal(0)

        return Response(day_totals)


class ElectricityLiveView(APIView):
    """ Returns the current electricity usage. """
    def get(self, request):
        return Response(dsmr_consumption.services.live_electricity_consumption())


class GasLiveView(APIView):
    """ Returns the current gas usage. """
    def get(self, request):
        return Response(dsmr_consumption.services.live_gas_consumption())


class ElectricityConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ Lists electricity consumption. """
    FIELD = 'read_at'
    queryset = ElectricityConsumption.objects.all()
    serializer_class = ElectricityConsumptionSerializer
    filterset_class = ElectricityConsumptionFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class GasConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ Lists gas consumption. """
    FIELD = 'read_at'
    queryset = GasConsumption.objects.all()
    serializer_class = GasConsumptionSerializer
    filterset_class = GasConsumptionFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class DayStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ Lists day statistics. """
    FIELD = 'day'
    queryset = DayStatistics.objects.all()
    serializer_class = DayStatisticsSerializer
    filterset_class = DayStatisticsFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class HourStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ Lists hour statistics. """
    FIELD = 'hour_start'
    queryset = HourStatistics.objects.all()
    serializer_class = HourStatisticsSerializer
    filterset_class = HourStatisticsFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class VersionView(APIView):
    """ Returns the current version of DSMR-reader. """
    def get(self, request):
        return Response({
            'version': '{}.{}.{}'.format(* settings.DSMRREADER_RAW_VERSION[:3]),
        })
