from decimal import Decimal
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

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--ack-to-mess-up-my-data',
            action='store_true',
            dest='acked_warning',
            default=False,
            help=_('Required option to acknowledge you that you WILL mess up your data with this.')
        )

    def handle(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        if not settings.DEBUG:
            raise CommandError(_('Intended usage is NOT production! Only allowed when DEBUG = True'))

        if not options.get('acked_warning'):
            raise CommandError(_('Intended usage is NOT production! Force by using --ack-to-mess-up-my-data'))

        self._randomize()

    def _randomize(self):
        """ Generates 'random' stats data by altering existing ones. """
        factor = Decimal(random.random())  # Between 0.0 and 1.0, change every day.
        print('Using existing consumption as base, multiplied by {}'.format(factor))

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
