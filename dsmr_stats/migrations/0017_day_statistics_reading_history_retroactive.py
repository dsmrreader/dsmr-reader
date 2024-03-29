# Generated by Django 3.1.7 on 2021-02-24 20:29

from django.db import migrations


def regenerate_data(apps, schema_editor):
    """Try to find any historic data for day statistics meter positions."""
    DayStatistics = apps.get_model("dsmr_stats", "DayStatistics")

    import dsmr_consumption.services
    import dsmr_backend.services.backend

    if dsmr_backend.services.backend.is_recent_installation():
        # Skip for new installations.
        return

    # No DB index, but should be fine.
    days = DayStatistics.objects.filter(electricity1_reading=None)
    day_count = days.count()
    x = 0

    for current in days:
        x += 1
        print(
            "Data migration: Retroactively adding reading meter positions for day statistics: {} ({}/{})".format(
                current.day, x, day_count
            )
        )

        try:
            day_consumption = dsmr_consumption.services.day_consumption(day=current.day)
        except LookupError:
            print(" - No data found for {}, skipping...".format(current.day))
            continue

        current.electricity1_reading = day_consumption["electricity1_start"]
        current.electricity2_reading = day_consumption["electricity2_start"]
        current.electricity1_returned_reading = day_consumption[
            "electricity1_returned_start"
        ]
        current.electricity2_returned_reading = day_consumption[
            "electricity2_returned_start"
        ]
        current.gas_reading = day_consumption.get("gas_start")
        current.save()


def revert_regenerated_data(apps, schema_editor):
    DayStatistics = apps.get_model("dsmr_stats", "DayStatistics")
    DayStatistics.objects.all().update(
        electricity1_reading=None,
        electricity2_reading=None,
        electricity1_returned_reading=None,
        electricity2_returned_reading=None,
        gas_reading=None,
    )


class Migration(migrations.Migration):
    operations = [migrations.RunPython(regenerate_data, revert_regenerated_data)]

    dependencies = [
        ("dsmr_stats", "0016_day_statistics_reading_history"),
    ]
