from decimal import Decimal

from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.conf import settings

from dsmr_api.schemas import DsmrReaderSchema
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_consumption.serializers.consumption import ElectricityConsumptionSerializer, GasConsumptionSerializer, \
    EnergySupplierPriceSerializer
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption
from dsmr_datalogger.models.statistics import MeterStatistics
from dsmr_datalogger.serializers.statistics import MeterStatisticsSerializer
from dsmr_stats.serializers.statistics import DayStatisticsSerializer, HourStatisticsSerializer
from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_datalogger.serializers.reading import DsmrReadingSerializer
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_api.filters import DsmrReadingFilter, DayStatisticsFilter, ElectricityConsumptionFilter, \
    GasConsumptionFilter, HourStatisticsFilter, EnergySupplierPriceFilter
import dsmr_consumption.services
import dsmr_backend.services.backend
import dsmr_datalogger.signals


class DsmrReadingViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    list:
    Retrieves any readings stored. The readings are either constructed from incoming telegrams or were created using
    this API.

    ### Query parameters
    - *Only mandatory when explicitly marked with the **required** label. Can be omitted otherwise.*
    - ``limit`` / ``offset``: Pagination for iterating when having large result sets.
    - ``ordering``: Order by either ``timestamp`` (ASC) or ``-timestamp`` (DESC).
    - ``timestamp__gte`` / ``timestamp__lte``: Can be used for generic filtering the results \
    returned by reading timestamp with the given datetime as placeholder `X` below. Note the ``Y-m-d HH:MM:SS`` \
    format for `X`, in the local timezone. **Should be changed to ISO 8601 some day, supporting timezone hints.**
    - ⚠️ **Deprecated** ~``timestamp``: Reading timestamp must **exactly match** the given value (``Y-m-d HH:MM:SS``).~

    ### Changes
    - Deprecated the ``timestamp`` query parameter in DSMR-reader v5.3

    ### Request samples
    ```
    // Fetching the latest reading created.
    GET /api/v2/consumption/energy-supplier-prices?ordering=-timestamp&limit=1

    // Get all readings of a specific "day", presuming that day is 15 January 2022.
    GET /api/v2/datalogger/dsmrreading?timestamp__gte=2022-01-15 00:00:00&timestamp__lte=2022-01-15 23:59:59
    ```


    create:
    Creates a reading from separate values, omitting the need for the original telegram.

    ### Notes
    - This requires you to **manually parse** any telegrams, e.g. when using ``dsmr_parser`` or a similar tool.
    - Readings are processed *simultaneously* by the background process. So inserting readings retroactively *might*
    cause undesired results due to side effects. *If your stats are not correctly after regenerating, see below,
    try it again while having your datalogger disabled.*
    - Inserting historic data might require you to **delete all aggregated data** as well, using:

    ```
    sudo su - postgres
    psql dsmrreader

    truncate dsmr_consumption_electricityconsumption;
    truncate dsmr_consumption_gasconsumption;
    truncate dsmr_stats_daystatistics;
    truncate dsmr_stats_hourstatistics;

    // This query can take a long time!
    update dsmr_datalogger_dsmrreading set processed = False;

    // This will process all readings again, from the very first start, and aggregate them once more.
    // It might take a long time, depending on your total reading count stored and hardware used.
    ```
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
    Retrieve meter statistics extracted by the datalogger. Also contains the latest telegram read for convenience.

    ### Query parameters
    - *Only mandatory when explicitly marked with the **required** label. Can be omitted otherwise.*
    - Do **not use** ``ordering``, as it's a faulty query parameter that should not be there nor works at all!


    partial_update:
    Manually update any meter statistics fields.

    ### Notes
    - Only use this when you're **not** using the built-in datalogger **nor** the v1 telegram API. \
    *It should auto-update otherwise!*
    """
    schema = DsmrReaderSchema(get='Retrieve meter statistics', patch='Update meter statistics')
    serializer_class = MeterStatisticsSerializer

    def get_queryset(self):  # pragma: nocover
        """ @see https://github.com/carltongibson/django-filter/issues/966#issuecomment-734971862 """
        if getattr(self, "swagger_fake_view", False):
            return MeterStatistics.objects.none()

    def get_object(self):
        # This is a nice combo with django-solo, as it fits perfectly for a singleton retriever and updater!
        return MeterStatistics.get_solo()


class EnergySupplierPriceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves the energy supplier prices (contracts).

    ### Notes
    - These are the contracts manually entered in DSMR-reader's admin interface. Can be used for manual
    calculations.

    > *E.g. fetching any contracts active today, then fetch all day statistics filtered by the contract's start/end,
    finally summing up the total consumption for that contract. Similar to DSMR-reader's GUI regarding contact totals.*

    ### Query parameters
    - *Only mandatory when explicitly marked with the **required** label. Can be omitted otherwise.*
    - ``limit`` / ``offset``: Optional pagination. Probably not needed unless you have *a lot* of contracts.
    - ``ordering``: Order by either ``start`` (ASC), ``-start`` (DESC), ``end`` (ASC) or ``-end`` (DESC).
    - ``start__gte`` / ``start__lte`` / ``end__gte`` / ``end__lte``: Can be used for generic filtering the results \
    returned by contracts' start/end with the given date as placeholder `X` below. Note the ``Y-m-d`` format for `X`.

    ### Changes
    - This endpoint was added in DSMR-reader v5.3

    ### Request samples
    ```
    // Get the most recent contract, based on its start date.
    GET /api/v2/consumption/energy-supplier-prices?ordering=-start&limit=1

    // Get all contracts active/applying to "today", presuming "today" is 15 June 2022.
    GET /api/v2/consumption/energy-supplier-prices?start__lte=2022-06-15&end__gte=2022-06-15
    ```
    """
    schema = DsmrReaderSchema(get='Retrieve energy supplier prices')
    queryset = EnergySupplierPrice.objects.all()
    serializer_class = EnergySupplierPriceSerializer
    filterset_class = EnergySupplierPriceFilter
    ordering_fields = ('start', 'end')
    ordering = 'start'


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
        today = timezone.localtime(timezone.now()).date()

        try:
            day_totals = dsmr_consumption.services.day_consumption(day=today)
        except LookupError:
            return Response('No electricity readings found for: {}'.format(today))

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
    """
    Retrieves any data regarding electricity consumption. This is based on the readings processed.

    ### Query parameters
    - *Only mandatory when explicitly marked with the **required** label. Can be omitted otherwise.*
    - ``limit`` / ``offset``: Pagination for iterating when having large result sets.
    - ``ordering``: Order by either ``read_at`` (ASC) or ``-read_at`` (DESC).
    - ``read_at__gte`` / ``read_at__lte``: Can be used for generic filtering the results \
    returned by consumption timestamp with the given datetime as placeholder `X` below. Note the ``Y-m-d HH:MM:SS`` \
    format for `X`, in the local timezone. **Should be changed to ISO 8601 some day, supporting timezone hints.**
    - ⚠️ **Deprecated** ~`read_at`: Consumption timestamp must **exactly match** the given value (``Y-m-d HH:MM:SS``).~

    ### Changes
    - Deprecated the ``read_at`` query parameter in DSMR-reader v5.3
    """
    schema = DsmrReaderSchema(get='Retrieve electricity consumption')
    FIELD = 'read_at'
    queryset = ElectricityConsumption.objects.all()
    serializer_class = ElectricityConsumptionSerializer
    filterset_class = ElectricityConsumptionFilter
    ordering_fields = (FIELD, )
    ordering = FIELD


class GasConsumptionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Retrieves any data regarding gas consumption. This is based on the readings processed.

    ### Query parameters
    - *Only mandatory when explicitly marked with the **required** label. Can be omitted otherwise.*
    - ``limit`` / ``offset``: Pagination for iterating when having large result sets.
    - ``ordering``: Order by either ``read_at`` (ASC) or ``-read_at`` (DESC).
    - ``read_at__gte`` / ``read_at__lte``: Can be used for generic filtering the results \
    returned by consumption timestamp with the given datetime as placeholder `X` below. Note the ``Y-m-d HH:MM:SS`` \
    format for `X`, in the local timezone. **Should be changed to ISO 8601 some day, supporting timezone hints.**
    - ⚠️ **Deprecated** ~`read_at`: Consumption timestamp must **exactly match** the given value (``Y-m-d HH:MM:SS``).~

    ### Changes
    - Deprecated the ``read_at`` query parameter in DSMR-reader v5.3
    """
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

    ### Notes
    - These are automatically generated a few hours after midnight, based on the consumption data.

    ### Query parameters
    - *Only mandatory when explicitly marked with the **required** label. Can be omitted otherwise.*
    - ``limit`` / ``offset``: Pagination for iterating when having large result sets.
    - ``ordering``: Order by either ``day`` (ASC) or ``-day`` (DESC).
    - ``day__gte`` / ``day__lte``: Can be used for generic filtering the results \
    returned by dates with the given date as placeholder `X` below.  ote the ``Y-m-d`` format for `X`.
    - ⚠️ **Deprecated** ~`day`: Date must **exactly match** the given value (``Y-m-d HH:MM:SS``).~

    ### Changes
    - Deprecated the ``day`` query parameter in DSMR-reader v5.3


    create:
    Creates statistics for a day, overriding any DSMR-reader internals.

    ### Notes
    - Should only be used to import historic data.
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
    Retrieves any aggregated hour statistics, as displayed in the Archive.

    ### Notes
    - These are automatically generated a few hours after midnight, based on the consumption data.

    ### Query parameters
    - *Only mandatory when explicitly marked with the **required** label. Can be omitted otherwise.*
    - ``limit`` / ``offset``: Pagination for iterating when having large result sets.
    - ``ordering``: Order by either ``hour_start`` (ASC) or ``-hour_start`` (DESC).
    - ``hour_start__gte`` / ``hour_start__lte``: Can be used for generic filtering the results \
    returned by hour start timestamp with the given datetime as placeholder `X` below. Note the ``Y-m-d HH:MM:SS`` \
    format for `X`, in the local timezone. **Should be changed to ISO 8601 some day, supporting timezone hints.**
    - ⚠️ **Deprecated** ~`hour_start`: Hour start timestamp must **exactly match** the given value (`Y-m-d HH:MM:SS`).~

    ### Changes
    - Deprecated the ``hour_start`` query parameter in DSMR-reader v5.3
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
