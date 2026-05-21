import bisect
import datetime
import sys
from decimal import Decimal
from typing import Dict, List, Optional

from django.utils import timezone

import dsmr_consumption.services
from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_consumption.models.energysupplier import EnergySupplierPrice
from dsmr_stats.models.statistics import DayStatistics, HourStatistics


def recalculate_statistics_from_meter_positions(dry_run: bool = False, batch_size: int = 90) -> None:  # noqa: C901
    """Retroactively recalculates DayStatistics totals using stored meter positions (fixes #1770).

    Processes days newest-first in batches of `batch_size` to limit memory use.
    In write mode, price contracts are resolved in Python from a single prefetched
    queryset and modified records are flushed with bulk_update once per batch.
    """
    today = timezone.localtime(timezone.now()).date()

    all_days: List[datetime.date] = list(
        DayStatistics.objects.filter(day__lt=today).order_by("-day").values_list("day", flat=True)
    )

    # Prefetch all price contracts once to avoid one SELECT per day.
    all_prices: List[EnergySupplierPrice] = list(EnergySupplierPrice.objects.all())

    updated = 0
    unchanged = 0
    skipped = 0
    total = len(all_days)
    processed = 0

    for batch_start in range(0, total, batch_size):
        batch_days = all_days[batch_start : batch_start + batch_size]

        # Fetch current batch records plus their next-day neighbours for delta calculation.
        next_days = [d + datetime.timedelta(days=1) for d in batch_days]
        records: Dict[datetime.date, DayStatistics] = {
            r.day: r for r in DayStatistics.objects.filter(day__in=set(batch_days) | set(next_days))
        }

        to_save: List[DayStatistics] = []

        for day in batch_days:
            current_record = records.get(day)
            if current_record is None:
                processed += 1
                _print_progress(processed, total)
                continue

            next_record = records.get(day + datetime.timedelta(days=1))

            if next_record is None:
                print("\n - [SKIP] No next-day record for: {}".format(day))
                skipped += 1
                processed += 1
                continue

            deltas = _electricity_deltas(current_record, next_record)
            if deltas is None:
                skipped += 1
                processed += 1
                continue

            new_e1, new_e2, new_e1_ret, new_e2_ret = deltas
            new_gas = _gas_delta(current_record, next_record)

            try:
                prices = _resolve_prices(day=current_record.day, all_prices=all_prices)
            except EnergySupplierPrice.DoesNotExist:
                if not dry_run:
                    print("\n   [!] No prices found for {}, using zero fallback".format(current_record.day))
                prices = dsmr_consumption.services.get_fallback_prices()

            fixed_cost = dsmr_consumption.services.round_decimal(prices.fixed_daily_cost)
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

            changed = (
                new_e1 != current_record.electricity1
                or new_e2 != current_record.electricity2
                or new_e1_ret != current_record.electricity1_returned
                or new_e2_ret != current_record.electricity2_returned
                or (new_gas is not None and new_gas != current_record.gas)
                or electricity1_cost != current_record.electricity1_cost
                or electricity2_cost != current_record.electricity2_cost
                or fixed_cost != current_record.fixed_cost
                or total_cost != current_record.total_cost
            )

            if not changed:
                unchanged += 1
                processed += 1
                _print_progress(processed, total)
                continue

            suffix = " [DRY RUN]" if dry_run else ""
            print("\n - Recalculating: {}{}".format(current_record.day, suffix))
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
            if electricity1_cost != current_record.electricity1_cost:
                print("   electricity1_cost:     {} -> {}".format(current_record.electricity1_cost, electricity1_cost))
            if electricity2_cost != current_record.electricity2_cost:
                print("   electricity2_cost:     {} -> {}".format(current_record.electricity2_cost, electricity2_cost))
            if fixed_cost != current_record.fixed_cost:
                print("   fixed_cost:            {} -> {}".format(current_record.fixed_cost, fixed_cost))
            if total_cost != current_record.total_cost:
                print("   total_cost:            {} -> {}".format(current_record.total_cost, total_cost))

            if not dry_run:
                _apply_recalculated_day(
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
                to_save.append(current_record)

            updated += 1
            processed += 1

        if to_save:
            _bulk_update_day_statistics(to_save)

        _print_progress(processed, total)

    print("\nDone. Updated: {}, Unchanged: {}, Skipped: {}".format(updated, unchanged, skipped))


def _print_progress(current: int, total: int, width: int = 40) -> None:
    if not sys.stdout.isatty():
        return
    filled = int(width * current / total) if total else width
    bar = "#" * filled + "." * (width - filled)
    pct = int(100 * current / total) if total else 100
    print("\r[{}] {}/{} ({}%)".format(bar, current, total, pct), end="", flush=True)


def recalculate_hour_statistics(dry_run: bool = False, batch_size: int = 2160) -> None:  # noqa: C901
    """Retroactively recalculates HourStatistics electricity totals using cross-boundary anchors (fixes #1770).

    Processes hours newest-first in batches of `batch_size`. Per batch, all required
    ElectricityConsumption anchor records are fetched in two queries (window + preceding record),
    then resolved via binary search — avoiding two DB queries per hour.
    In write mode, changed records are flushed with bulk_update once per batch.
    """
    updated = 0
    unchanged = 0
    skipped = 0

    all_hour_ids: List[int] = list(HourStatistics.objects.order_by("-hour_start").values_list("id", flat=True))
    total = len(all_hour_ids)
    processed = 0

    for batch_start in range(0, total, batch_size):
        batch_ids = all_hour_ids[batch_start : batch_start + batch_size]
        hours = list(HourStatistics.objects.filter(id__in=batch_ids).order_by("hour_start"))

        if not hours:
            continue

        window_start = hours[0].hour_start
        window_end = hours[-1].hour_start + timezone.timedelta(hours=1)

        # Fetch EC records that span this batch's time window plus the one just before it.
        ec_before = ElectricityConsumption.objects.filter(read_at__lt=window_start).order_by("-read_at").first()
        ec_in_window: List[ElectricityConsumption] = list(
            ElectricityConsumption.objects.filter(read_at__gte=window_start, read_at__lte=window_end).order_by(
                "read_at"
            )
        )

        all_ec: List[ElectricityConsumption] = ([ec_before] if ec_before else []) + ec_in_window
        ec_timestamps = [r.read_at for r in all_ec]

        to_save: List[HourStatistics] = []

        for hour in hours:
            hour_end = hour.hour_start + timezone.timedelta(hours=1)

            idx_start = bisect.bisect_right(ec_timestamps, hour.hour_start) - 1
            idx_end = bisect.bisect_right(ec_timestamps, hour_end) - 1

            if idx_start < 0 or idx_end < 0:
                print("\n - [SKIP] Missing anchor(s) for: {}".format(timezone.localtime(hour.hour_start)))
                skipped += 1
                processed += 1
                continue

            anchor_start = all_ec[idx_start]
            anchor_end = all_ec[idx_end]

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
                unchanged += 1
                processed += 1
                _print_progress(processed, total)
                continue

            suffix = " [DRY RUN]" if dry_run else ""
            print("\n - Recalculating: {}{}".format(timezone.localtime(hour.hour_start), suffix))
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
                to_save.append(hour)

            updated += 1
            processed += 1

        if to_save:
            HourStatistics.objects.bulk_update(
                to_save, ["electricity1", "electricity2", "electricity1_returned", "electricity2_returned"]
            )

        _print_progress(processed, total)

    print("\nDone. Updated: {}, Unchanged: {}, Skipped: {}".format(updated, unchanged, skipped))


def _resolve_prices(day: datetime.date, all_prices: List[EnergySupplierPrice]) -> EnergySupplierPrice:
    """Resolves the applicable price contract(s) for `day` from a pre-fetched list.

    Mirrors dsmr_consumption.services.get_day_prices() but operates entirely in Python,
    avoiding a database round-trip per day.
    """
    contracts = [p for p in all_prices if p.start <= day <= p.end]

    if len(contracts) == 1:
        return contracts[0]

    if not contracts:
        raise EnergySupplierPrice.DoesNotExist()

    combined = dsmr_consumption.services.get_fallback_prices()

    for field in (
        "electricity_delivered_1_price",
        "electricity_delivered_2_price",
        "gas_price",
        "electricity_returned_1_price",
        "electricity_returned_2_price",
        "fixed_daily_cost",
    ):
        values = [getattr(c, field) for c in contracts if getattr(c, field) > 0]
        if len(values) == 1:
            setattr(combined, field, values[0])

    return combined


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


def _apply_recalculated_day(
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
    """Mutates `record` in-place; caller is responsible for persisting via bulk_update."""
    record.electricity1 = new_e1
    record.electricity2 = new_e2
    record.electricity1_returned = new_e1_ret
    record.electricity2_returned = new_e2_ret
    record.electricity1_cost = electricity1_cost
    record.electricity2_cost = electricity2_cost
    record.fixed_cost = fixed_cost
    record.total_cost = total_cost

    if new_gas is not None and new_gas_cost is not None:
        record.gas = new_gas
        record.gas_cost = new_gas_cost


def _bulk_update_day_statistics(records: List[DayStatistics]) -> None:
    fields = [
        "electricity1",
        "electricity2",
        "electricity1_returned",
        "electricity2_returned",
        "electricity1_cost",
        "electricity2_cost",
        "fixed_cost",
        "total_cost",
        "gas",
        "gas_cost",
    ]
    DayStatistics.objects.bulk_update(records, fields)


def recalculate_prices(batch_size: int = 365) -> None:
    """Retroactively sets the prices for all statistics. E.g. when the user has altered the prices in the past.

    Prefetches all price contracts once and accumulates changes for bulk_update per batch,
    avoiding one SELECT and one UPDATE per day.
    """
    all_prices: List[EnergySupplierPrice] = list(EnergySupplierPrice.objects.all())
    to_save: List[DayStatistics] = []
    total = DayStatistics.objects.count()
    processed = 0

    for current_day in DayStatistics.objects.order_by("-day").iterator(chunk_size=batch_size):
        try:
            prices = _resolve_prices(day=current_day.day, all_prices=all_prices)
        except EnergySupplierPrice.DoesNotExist:
            print("\n   [!] No prices found for this day, using zero fallback")
            prices = dsmr_consumption.services.get_fallback_prices()

        current_day.fixed_cost = prices.fixed_daily_cost
        current_day.electricity1_cost = dsmr_consumption.services.round_decimal(
            (current_day.electricity1 * prices.electricity_delivered_1_price)
            - (current_day.electricity1_returned * prices.electricity_returned_1_price)
        )
        current_day.electricity2_cost = dsmr_consumption.services.round_decimal(
            (current_day.electricity2 * prices.electricity_delivered_2_price)
            - (current_day.electricity2_returned * prices.electricity_returned_2_price)
        )

        total_cost = current_day.electricity1_cost + current_day.electricity2_cost + current_day.fixed_cost

        if current_day.gas is not None:
            current_day.gas_cost = dsmr_consumption.services.round_decimal(current_day.gas * prices.gas_price)
            total_cost += current_day.gas_cost

        current_day.total_cost = dsmr_consumption.services.round_decimal(total_cost)
        to_save.append(current_day)
        processed += 1
        _print_progress(processed, total)

        if len(to_save) >= batch_size:
            _bulk_update_day_price_fields(to_save)
            to_save = []

    if to_save:
        _bulk_update_day_price_fields(to_save)

    print("\nDone.")


def _bulk_update_day_price_fields(records: List[DayStatistics]) -> None:
    DayStatistics.objects.bulk_update(
        records,
        ["electricity1_cost", "electricity2_cost", "fixed_cost", "gas_cost", "total_cost"],
    )
