from decimal import Decimal
from time import sleep
import random

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db import models

from dsmr_stats.models.statistics import DayStatistics, HourStatistics
from dsmr_consumption.models.consumption import ElectricityConsumption
from dsmr_datalogger.models.reading import DsmrReading


class Command(BaseCommand):
    help = _('Alters any stats generate to fake data. DO NOT USE in production! Used for integration checks.')

    def handle(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        if not settings.DEBUG:
            raise CommandError(_('Intended usage is NOT production! Only allowed when DEBUG = True'))

        self._randomize()

    def _randomize(self):
        """ Generates 'random' stats data by altering existing ones. """
        factor = Decimal(random.random())  # Between 0.0 and 1.0, change every day.
        print('Using existing consumption as base, multiplied by {}'.format(factor))

        sleep(1)  # Allow to abort when random number sucks.

        print('Altering readings... (might take quite some time)')
        DsmrReading.objects.all().order_by('-pk').update(
            electricity_returned_1=models.F('electricity_delivered_1') * factor,
            electricity_returned_2=models.F('electricity_delivered_2') * factor,
            electricity_currently_returned=models.F('electricity_currently_delivered') * factor,
        )

        print('Altering electricity consumption... (might take quite some time as well)')
        ElectricityConsumption.objects.all().update(
            returned_1=models.F('delivered_1') * factor,
            returned_2=models.F('delivered_2') * factor,
            currently_returned=models.F('currently_delivered') * factor,
            phase_currently_delivered_l1=models.F('currently_delivered') * factor,  # Split.
            phase_currently_delivered_l2=models.F('currently_delivered') * (1 - factor),  # Remainder of split.
            phase_currently_delivered_l3=0.005,  # Weird constant, to keep it simple.
            phase_currently_returned_l1=models.F('currently_returned') * factor,  # Split.
            phase_currently_returned_l2=models.F('currently_returned') * (1 - factor),  # Remainder of split.
            phase_currently_returned_l3=0.005,  # Weird constant, to keep it simple.
        )

        print('Altering hour statistics...')
        HourStatistics.objects.all().update(
            electricity1_returned=models.F('electricity1') * factor,
            electricity2_returned=models.F('electricity2') * factor,
        )

        print('Altering day statistics...')
        DayStatistics.objects.all().update(
            electricity1_returned=models.F('electricity1') * factor,
            electricity2_returned=models.F('electricity2') * factor,
        )
        print('Done!')
