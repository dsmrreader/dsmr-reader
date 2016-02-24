# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.utils import timezone


def recalculate_gas_consumption(apps, schema):
    """ Restores consumption data which was incomplete due to bug in #40. """
    GasConsumption = apps.get_model('dsmr_consumption', 'GasConsumption')
    DsmrReading = apps.get_model('dsmr_datalogger', 'DsmrReading')
    broken_since = timezone.make_aware(timezone.datetime(2016, 2, 22))

    print()
    print('Recalculating gas consumption since {}'.format(broken_since))

    for current_consumption in GasConsumption.objects.filter(read_at__gt=broken_since).order_by('read_at'):
        print()
        print(' - {}: {}'.format(current_consumption.read_at, current_consumption.currently_delivered))

        if current_consumption.currently_delivered > 0:
            print(' --- Not empty, must be OK')
            continue

        print(' --- EMPTY value, rechecking source reading...')

        # Find the a reading of the current consumption hour. Doesn't matter which one.
        source_reading = DsmrReading.objects.filter(
            # Offset is one hour later due to start of hour.
            extra_device_timestamp=current_consumption.read_at + timezone.timedelta(hours=1)
        )[0]

        # Find previous reading to calculate diff.
        previous_consumption = GasConsumption.objects.get(
            read_at=current_consumption.read_at - timezone.timedelta(hours=1)
        )
        actual_diff = source_reading.extra_device_delivered - previous_consumption.delivered

        print(' >>> Updating hour gas consumption to {}'.format(actual_diff))
        current_consumption.currently_delivered = actual_diff
        current_consumption.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dsmr_consumption', '0003_realign_gas_read_at'),
        ('dsmr_datalogger', '0003_split_dsmr_reading_fields'),
    ]

    operations = [
        migrations.RunPython(recalculate_gas_consumption)
    ]
