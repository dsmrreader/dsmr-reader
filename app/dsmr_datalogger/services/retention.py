import logging

from django.db.models.functions.datetime import TruncHour
from django.db.models.aggregates import Count
from django.utils import timezone
from django.conf import settings
import pytz

from dsmr_backend.models.schedule import ScheduledProcess
from dsmr_datalogger.models.reading import DsmrReading
from dsmr_datalogger.models.settings import RetentionSettings
from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption


logger = logging.getLogger("dsmrreader")


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

    retention_date = timezone.now() - timezone.timedelta(
        hours=retention_settings.data_retention_in_hours
    )
    data_to_clean_up = False

    # We need to force UTC here, to avoid AmbiguousTimeError's on DST changes.
    timezone.activate(pytz.UTC)

    for base_queryset, datetime_field in MODELS_TO_CLEANUP.items():
        hours_to_cleanup = (
            base_queryset.filter(**{"{}__lt".format(datetime_field): retention_date})
            .annotate(item_hour=TruncHour(datetime_field))
            .values("item_hour")
            .annotate(item_count=Count("id"))
            .order_by()
            .filter(item_count__gt=ITEM_COUNT_PER_HOUR)
            .order_by("item_hour")
            .values_list("item_hour", flat=True)[
                : settings.DSMRREADER_RETENTION_MAX_CLEANUP_HOURS_PER_RUN
            ]
        )

        hours_to_cleanup = list(hours_to_cleanup)  # Force evaluation.

        if not hours_to_cleanup:
            continue

        data_to_clean_up = True

        for current_hour in hours_to_cleanup:
            # Fetch all data per hour.
            data_set = base_queryset.filter(
                **{
                    "{}__gte".format(datetime_field): current_hour,
                    "{}__lt".format(datetime_field): current_hour
                    + timezone.timedelta(hours=1),
                }
            )

            # Extract the first/last item, so we can exclude it.
            # NOTE: Want to alter this? Please update ITEM_COUNT_PER_HOUR above as well!
            keeper_pks = [
                data_set.order_by(datetime_field)[0].pk,
                data_set.order_by("-{}".format(datetime_field))[0].pk,
            ]

            # Now drop all others.
            logger.debug(
                "Retention: Cleaning up: %s (%s)",
                current_hour,
                data_set[0].__class__.__name__,
            )
            data_set.exclude(pk__in=keeper_pks).delete()

    timezone.deactivate()

    # Delay for a bit, as there is nothing to do.
    if not data_to_clean_up:
        scheduled_process.delay(hours=12)
