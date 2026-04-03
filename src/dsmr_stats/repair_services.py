import datetime
from decimal import Decimal
from typing import Dict, List, Optional

from django.utils import timezone

import dsmr_consumption.services
from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import DayStatistics, HourStatistics


def recalculate_statistics_from_meter_positions(dry_run: bool = False, batch_size: int = 365) -> None:  # noqa: C901
    """Retroactively recalculates DayStatistics totals using stored meter positions (fixes #1770).

    Processes days newest-first in batches of `batch_size` to limit memory use.
    """
    today = timezone.localtime(timezone.now()).date()

    all_days: List[datetime.date] = list(
        DayStatistics.objects.filter(day__lt=today).order_by("-day").values_list("day", flat=True)
    )

    skipped = 0
    recalculated = 0

    for batch_start in range(0, len(all_days), batch_size):
        batch_days = all_days[batch_start : batch_start + batch_size]

        # Fetch current batch records plus their next-day neighbours for delta calculation.
        next_days = [d + datetime.timedelta(days=1) for d in batch_days]
        records: Dict[datetime.date, DayStatistics] = {
            r.day: r
            for r in DayStatistics.objects.filter(day__in=set(batch_days) | set(next_days))
        }

        for day in batch_days:
            current_record = records.get(day)
            if current_record is None:
                continue

            next_record = records.get(day + datetime.timedelta(days=1))

            if next_record is None:
                print(" - [SKIP] No next-day record for: {}".format(day))
                skipped += 1
                continue

            deltas = _electricity_deltas(current_record, next_record)
            if deltas is None:
                skipped += 1
                continue

            new_e1, new_e2, new_e1_ret, new_e2_ret = deltas
            new_gas = _gas_delta(current_record, next_record)

            try:
                prices = dsmr_consumption.services.get_day_prices(day=current_record.day)
            except EnergySupplierPrice.DoesNotExist:
                print("   [!] No prices found for {}, using zero fallback".format(current_record.day))
                prices = dsmr_consumption.services.get_fallback_prices()

            fixed_cost = prices.fixed_daily_cost
            electricity1_cost = dsmr_consumption.services.round_decimal(
                (new_e1 * prices.electricity_delivered_1_price) - (new_e1_ret * prices.electricity_returned_1_price)
            )
            electricity2_cost = dsmr_consumption.services.round_decimal(
                (new_e2 * prices.electricity_delivered_2_price) - (new_e2_ret * prices.electricity_returned_2_price)
            )
            total_cost = electricity1_cost + electricity2_cost + fixed_cost

            new_gas_cost: Optional[Decimal] = None
            if new_gas is not None:
                new_gas_cost = dsmr_consumption.services.round_decimal(new_gas * prices.gas_price)
                total_cost += new_gas_cost
            elif current_record.gas_cost is not None:
                total_cost += current_record.gas_cost

            total_cost = dsmr_consumption.services.round_decimal(total_cost)

            suffix = " [DRY RUN]" if dry_run else ""
            print(" - Recalculating: {}{}".format(current_record.day, suffix))
            if new_e1 != current_record.electricity1:
                print("   electricity1:          {} -> {}".format(current_record.electricity1, new_e1))
            if new_e2 != current_record.electricity2:
                print("   electricity2:          {} -> {}".format(current_record.electricity2, new_e2))
            if new_e1_ret != current_record.electricity1_returned:
                print("   electricity1_returned: {} -> {}".format(current_record.electricity1_returned, new_e1_ret))
            if new_e2_ret != current_record.electricity2_returned:
                print("   electricity2_returned: {} -> {}".format(current_record.electricity2_returned, new_e2_ret))
            if new_gas is not None and new_gas != current_record.gas:
                print("   gas:                   {} -> {}".format(current_record.gas, new_gas))

            if not dry_run:
                _save_recalculated_day(
                    current_record,
                    new_e1,
                    new_e2,
                    new_e1_ret,
                    new_e2_ret,
                    electricity1_cost,
                    electricity2_cost,
                    fixed_cost,
                    total_cost,
                    new_gas,
                    new_gas_cost,
                )

            recalculated += 1

    print("\nDone. Recalculated: {}, Skipped: {}".format(recalculated, skipped))


def recalculate_hour_statistics(dry_run: bool = False, batch_size: int = 168) -> None:
    """Retroactively recalculates HourStatistics electricity totals using cross-boundary anchors (fixes #1770).

    Processes hours newest-first using a server-side cursor of `batch_size` to limit memory use.
    """
    skipped = 0
    recalculated = 0

    for hour in HourStatistics.objects.order_by("-hour_start").iterator(chunk_size=batch_size):
        hour_end = hour.hour_start + timezone.timedelta(hours=1)

        anchor_start = ElectricityConsumption.objects.filter(read_at__lt=hour.hour_start).order_by("read_at").last()
        anchor_end = ElectricityConsumption.objects.filter(read_at__lt=hour_end).order_by("read_at").last()

        if anchor_start is None or anchor_end is None:
            print(" - [SKIP] Missing anchor(s) for: {}".format(timezone.localtime(hour.hour_start)))
            skipped += 1
            continue

        new_e1 = anchor_end.delivered_1 - anchor_start.delivered_1
        new_e2 = anchor_end.delivered_2 - anchor_start.delivered_2
        new_e1_ret = anchor_end.returned_1 - anchor_start.returned_1
        new_e2_ret = anchor_end.returned_2 - anchor_start.returned_2

        changed = (
            new_e1 != hour.electricity1
            or new_e2 != hour.electricity2
            or new_e1_ret != hour.electricity1_returned
            or new_e2_ret != hour.electricity2_returned
        )

        if not changed:
            recalculated += 1
            continue

        suffix = " [DRY RUN]" if dry_run else ""
        print(" - Recalculating: {}{}".format(timezone.localtime(hour.hour_start), suffix))
        if new_e1 != hour.electricity1:
            print("   electricity1:          {} -> {}".format(hour.electricity1, new_e1))
        if new_e2 != hour.electricity2:
            print("   electricity2:          {} -> {}".format(hour.electricity2, new_e2))
        if new_e1_ret != hour.electricity1_returned:
            print("   electricity1_returned: {} -> {}".format(hour.electricity1_returned, new_e1_ret))
        if new_e2_ret != hour.electricity2_returned:
            print("   electricity2_returned: {} -> {}".format(hour.electricity2_returned, new_e2_ret))

        if not dry_run:
            hour.electricity1 = new_e1
            hour.electricity2 = new_e2
            hour.electricity1_returned = new_e1_ret
            hour.electricity2_returned = new_e2_ret
            hour.save(update_fields=["electricity1", "electricity2", "electricity1_returned", "electricity2_returned"])

        recalculated += 1

    print("\nDone. Recalculated: {}, Skipped: {}".format(recalculated, skipped))


def _electricity_deltas(current_record: DayStatistics, next_record: DayStatistics) -> Optional[tuple]:
    """Returns (e1, e2, e1r, e2r) deltas, or None when the day must be skipped."""
    readings = [
        current_record.electricity1_reading,
        current_record.electricity2_reading,
        current_record.electricity1_returned_reading,
        current_record.electricity2_returned_reading,
        next_record.electricity1_reading,
        next_record.electricity2_reading,
        next_record.electricity1_returned_reading,
        next_record.electricity2_returned_reading,
    ]
    if any(v is None for v in readings):
        print(" - [SKIP] NULL electricity reading(s) for: {}".format(current_record.day))
        return None

    new_e1 = next_record.electricity1_reading - current_record.electricity1_reading  # type: ignore[operator]
    new_e2 = next_record.electricity2_reading - current_record.electricity2_reading  # type: ignore[operator]
    cur_e1r = current_record.electricity1_returned_reading
    cur_e2r = current_record.electricity2_returned_reading
    new_e1_ret = next_record.electricity1_returned_reading - cur_e1r  # type: ignore[operator]
    new_e2_ret = next_record.electricity2_returned_reading - cur_e2r  # type: ignore[operator]

    if any(v < 0 for v in [new_e1, new_e2, new_e1_ret, new_e2_ret]):
        print(" - [WARN] Negative electricity delta (possible meter replacement) for: {}".format(current_record.day))
        return None

    return new_e1, new_e2, new_e1_ret, new_e2_ret


def _gas_delta(current_record: DayStatistics, next_record: DayStatistics) -> Optional[Decimal]:
    """Returns gas delta, or None when gas update must be skipped."""
    if current_record.gas_reading is None or next_record.gas_reading is None:
        return None
    delta = next_record.gas_reading - current_record.gas_reading
    if delta < 0:
        print(" - [WARN GAS] Negative gas delta for: {}, skipping gas update".format(current_record.day))
        return None
    return delta


def _save_recalculated_day(
    record: DayStatistics,
    new_e1: Decimal,
    new_e2: Decimal,
    new_e1_ret: Decimal,
    new_e2_ret: Decimal,
    electricity1_cost: Decimal,
    electricity2_cost: Decimal,
    fixed_cost: Decimal,
    total_cost: Decimal,
    new_gas: Optional[Decimal],
    new_gas_cost: Optional[Decimal],
) -> None:
    record.electricity1 = new_e1
    record.electricity2 = new_e2
    record.electricity1_returned = new_e1_ret
    record.electricity2_returned = new_e2_ret
    record.electricity1_cost = electricity1_cost
    record.electricity2_cost = electricity2_cost
    record.fixed_cost = fixed_cost
    record.total_cost = total_cost

    update_fields = [
        "electricity1",
        "electricity2",
        "electricity1_returned",
        "electricity2_returned",
        "electricity1_cost",
        "electricity2_cost",
        "fixed_cost",
        "total_cost",
    ]

    if new_gas is not None and new_gas_cost is not None:
        record.gas = new_gas
        record.gas_cost = new_gas_cost
        update_fields += ["gas", "gas_cost"]

    record.save(update_fields=update_fields)
