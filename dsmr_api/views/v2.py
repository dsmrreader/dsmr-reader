from decimal import Decimal

from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.conf import settings

from dsmr_api.schemas import DsmrReaderSchema
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
import dsmr_backend.services.backend
import dsmr_datalogger.signals


class DsmrReadingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
    Retrieves any readings stored. The readings are either constructed from incoming telegrams or were created using
    this API.

    *For example, fetching the latest reading created:*

    ```
        limit: 1
        ordering: -timestamp
    ```

    **All parameters are optional**

    create:
    Creates a reading from separate values, omitting the need for the original telegram.

    # Note

    Readings are processed simultaneously by the background process. Therefor inserting readings retroactively might
    result in undesired results.

    Therefor inserting historic data might require you to delete all aggregated data using:

    ```
        sudo su - postgres
        psql dsmrreader

        truncate dsmr_consumption_electricityconsumption;
        truncate dsmr_consumption_gasconsumption;
        truncate dsmr_stats_daystatistics;
        truncate dsmr_stats_hourstatistics;

        # This query can take a long time!
        update dsmr_datalogger_dsmrreading set processed = False;
    ```

    This will process all readings again, from the very first start, and aggregate them (and will take a long time,
    depending on your reading count).

    *The datalogger may interfere. If your stats are not correctly after regenerating, try it again while having your
    datalogger disabled.*
    """
    schema = DsmrReaderSchema(get='Retrieve DSMR readings', post='Create DSMR reading')
    FIELD = 'timestamp'
    queryset = DsmrReading.objects.all()
    serializer_class = DsmrReadingSerializer
    filterset_class = DsmrReadingFilter
    ordering_fields = (FIELD, )
    ordering = FIELD

    def perform_create(self, serializer):
        """ Overwritten to support custom model creation signal."""
        new_instance = serializer.save()
        dsmr_datalogger.signals.dsmr_reading_created.send_robust(None, instance=new_instance)


class MeterStatisticsViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    retrieve:
    Retrieve meter statistics extracted by the datalogger.

    partial_update:
    Manually update any meter statistics fields. Only use this when you're not using the built-in datalogger (of v1
    telegram API).
    """
    schema = DsmrReaderSchema(get='Retrieve meter statistics', patch='Update meter statistics')
    serializer_class = MeterStatisticsSerializer

    def get_queryset(self):  # pragma: nocover
        """ @see https://github.com/carltongibson/django-filter/issues/966#issuecomment-734971862 """
        if getattr(self, "swagger_fake_view", False):
            return MeterStatistics.objects.none()

    def get_object(self):
        # This is a REALLY good combo with django-solo, as it fits perfectly for a singleton retriever and updater!
        return MeterStatistics.get_solo()


class TodayConsumptionView(APIView):
    """ Returns the consumption of the current day so far. """
    schema = DsmrReaderSchema(get='Retrieve today\'s consumption')
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
        except LookupError:
            return Response('Failed to find day totals')

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
    """ Returns the live electricity consumption, containing the same data as the Dashboard header. """
    schema = DsmrReaderSchema(get='Retrieve live electricity consumption')

    def get(self, request):
        return Response(dsmr_consumption.services.live_electricity_consumption())


class GasLiveView(APIView):
    """ Returns the latest gas consumption. """
    schema = DsmrReaderSchema(get='Retrieve live gas consumption')

    def get(self, request):
        return Response(dsmr_consumption.services.live_gas_consumption())


class ElectricityConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ Retrieves any data regarding electricity consumption. This is based on the readings processed. """
    schema = DsmrReaderSchema(get='Retrieve electricity consumption')
    FIELD = 'read_at'
    queryset = ElectricityConsumption.objects.all()
    serializer_class = ElectricityConsumptionSerializer
    filterset_class = ElectricityConsumptionFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class GasConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    """ Retrieves any data regarding gas consumption. This is based on the readings processed. """
    schema = DsmrReaderSchema(get='Retrieve gas consumption')
    FIELD = 'read_at'
    queryset = GasConsumption.objects.all()
    serializer_class = GasConsumptionSerializer
    filterset_class = GasConsumptionFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class DayStatisticsViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    """
    list:
    Retrieves any aggregated day statistics, as displayed in the Archive.

    ## Note

    *These are automatically generated a few hours after midnight.*

    create:
    Creates statistics for a day, overriding any DSMR-reader internals.

    ## Note
    *Should only be used to import historic data.*
    """
    schema = DsmrReaderSchema(get='Retrieve day statistics', post='Create day statistics')
    FIELD = 'day'
    queryset = DayStatistics.objects.all()
    serializer_class = DayStatisticsSerializer
    filterset_class = DayStatisticsFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class HourStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves any aggregated hour statistics.

    **Note**

    *These are generated a few hours after midnight.*
    """
    schema = DsmrReaderSchema(get='Retrieve hour statistics')
    FIELD = 'hour_start'
    queryset = HourStatistics.objects.all()
    serializer_class = HourStatisticsSerializer
    filterset_class = HourStatisticsFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class VersionView(APIView):
    """ Returns the version of DSMR-reader you are running. """
    schema = DsmrReaderSchema(get='Application version')

    def get(self, request):
        return Response({
            'version': '{}.{}.{}'.format(* settings.DSMRREADER_RAW_VERSION[:3]),
        })


class MonitoringIssuesView(APIView):
    """ Returns any monitoring issues found. Reflects the same (issue) data as displayed on the Status page. """
    schema = DsmrReaderSchema(get='Application monitoring')

    def get(self, request):
        issues = dsmr_backend.services.backend.request_monitoring_status()

        return Response({
            'problems': len(issues),
            'details': [x.serialize() for x in issues]
        })
