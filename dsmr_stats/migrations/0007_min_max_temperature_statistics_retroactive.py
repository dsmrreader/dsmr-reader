# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.db.models import Q


def regenerate_data(apps, schema_editor):
    DayStatistics = apps.get_model("dsmr_stats", "DayStatistics")

    # Only when we have at least one temperature reading which was not zero.
    if not DayStatistics.objects.filter(~Q(average_temperature=0)).exists():
        return

    print("")

    day_count = DayStatistics.objects.all().count()
    DayStatistics.objects.all().delete()

    import dsmr_stats.services

    for x in range(1, day_count + 1):
        # Just call analyze for each day. If we missed a day or so, the backend will regenerate it.
        print("Regenerating day: {} / {}".format(x, day_count))
        dsmr_stats.services.analyze()


class Migration(migrations.Migration):

    dependencies = [
        ("dsmr_stats", "0006_min_max_temperature_statistics"),
    ]

    operations = [migrations.RunPython(regenerate_data)]
