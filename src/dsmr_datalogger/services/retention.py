import logging
from datetime import datetime, timedelta

from django.core.cache import cache
from django.db.models import QuerySet
from django.db.models.functions.datetime import TruncHour
from django.db.models.aggregates import Count
from django.utils import timezone
from django.conf import settings
from zoneinfo import ZoneInfo

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import RetentionSettings
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption


logger = logging.getLogger("dsmrreader")

_CACHE_KEY_PREFIX = "retention_lower_bound"


def _cache_key(model_name: str) -> str:
    return f"{_CACHE_KEY_PREFIX}_{model_name}"


def clear_cache() -> None:
    """Clear all retention progress cache entries, e.g. after retention settings change."""
    cache.delete_many(
        [
            _cache_key("DsmrReading"),
            _cache_key("ElectricityConsumption"),
            _cache_key("GasConsumption"),
        ]
    )


def _cleanup_hour(
    base_queryset: QuerySet, datetime_field: str, current_hour: datetime, retention_date: datetime
) -> None:
    """Deletes all but the first and last item in the given hour, never touching data inside the retention window."""
    data_set = base_queryset.filter(
        **{
            "{}__gte".format(datetime_field): current_hour,
            "{}__lt".format(datetime_field): min(current_hour + timedelta(hours=1), retention_date),
        }
    )

    # Extract the first/last item, so we can exclude it. The pk breaks ties between equal timestamps.
    # NOTE: Want to alter this? Please update ITEM_COUNT_PER_HOUR in run() as well!
    first_item = data_set.order_by(datetime_field, "pk").first()
    last_item = data_set.order_by("-{}".format(datetime_field), "-pk").first()

    if first_item is None or last_item is None:
        logger.debug("Retention: Skipping hour without data: %s (%s)", current_hour, base_queryset.model.__name__)
        return

    logger.debug("Retention: Cleaning up: %s (%s)", current_hour, base_queryset.model.__name__)
    data_set.exclude(pk__in=[first_item.pk, last_item.pk]).delete()


def run(scheduled_process: ScheduledProcess) -> None:
    retention_settings = RetentionSettings.get_solo()

    if retention_settings.data_retention_in_hours == RetentionSettings.RETENTION_NONE:
        scheduled_process.disable()  # Changing the retention settings in the admin will re-activate it again.
        return

    # These models should be rotated with retention. Dict value is the datetime field used.
    ITEM_COUNT_PER_HOUR = 2
    MODELS_TO_CLEANUP = {
        DsmrReading.objects.processed(): "timestamp",
        ElectricityConsumption.objects.all(): "read_at",
        GasConsumption.objects.all(): "read_at",
    }

    retention_date = timezone.now() - timedelta(hours=retention_settings.data_retention_in_hours)
    data_to_clean_up = False

    # We need to force UTC here, to avoid AmbiguousTimeError's on DST changes.
    timezone.activate(ZoneInfo("UTC"))

    try:
        for base_queryset, datetime_field in MODELS_TO_CLEANUP.items():
            model_name = base_queryset.model.__name__
            lower_bound: datetime | None = cache.get(_cache_key(model_name))

            candidate_queryset = base_queryset.filter(**{"{}__lt".format(datetime_field): retention_date})

            if lower_bound is not None:
                candidate_queryset = candidate_queryset.filter(**{"{}__gte".format(datetime_field): lower_bound})

            hours_to_cleanup = (
                candidate_queryset.annotate(item_hour=TruncHour(datetime_field, tzinfo=ZoneInfo("UTC")))
                .values("item_hour")
                .annotate(item_count=Count(datetime_field))
                .order_by()
                .filter(item_count__gt=ITEM_COUNT_PER_HOUR)
                .order_by("item_hour")
                .values_list("item_hour", flat=True)[: settings.DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN]
            )

            # The hour is truncated in UTC by the database, so its wall-clock value is the UTC hour, whatever tzinfo the
            # database layer attached to it.
            hours_to_cleanup = [hour.replace(tzinfo=ZoneInfo("UTC")) for hour in hours_to_cleanup]  # Force evaluation.

            if not hours_to_cleanup:
                continue

            # Only flag more data pending when the batch was saturated, implying there may be more to process.
            if len(hours_to_cleanup) >= settings.DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN:
                data_to_clean_up = True

            for current_hour in hours_to_cleanup:
                _cleanup_hour(base_queryset, datetime_field, current_hour, retention_date)

                # Advance the lower bound per hour, so future runs skip already-processed history without ever
                # skipping hours that were not reached. The hour containing the cutoff is only partially cleaned and
                # stays eligible.
                if current_hour + timedelta(hours=1) <= retention_date:
                    cache.set(_cache_key(model_name), current_hour + timedelta(hours=1), timeout=None)
    finally:
        timezone.deactivate()

    # Delay for a bit, as there is nothing to do.
    if not data_to_clean_up:
        scheduled_process.delay(hours=12)
