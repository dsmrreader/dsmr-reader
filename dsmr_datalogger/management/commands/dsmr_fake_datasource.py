from unittest import mock
from datetime import datetime
import random
import time

from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.core.management import call_command
from decimal import Decimal, ROUND_UP


class Command(BaseCommand):
    help = _('Generates a FAKE reading. DO NOT USE in production! Used for integration checks.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--ack-to-mess-up-my-data',
            action='store_true',
            dest='acked_warning',
            default=False,
            help=_('Required option to acknowledge you that you WILL mess up your data with this.')
        )

    def handle(self, **options):
        if not options.get('acked_warning'):
            raise CommandError(_(
                'Intended usage is NOT production! Force by using --ack-to-mess-up-my-data'
            ))

        self._inject()

    @mock.patch('dsmr_datalogger.services.read_telegram')
    def _inject(self, read_telegram_mock):
        """ Calls the regular DSMR datalogger, but injects it with random data using mock. """

        # Prepare some random data, but which makes sense.
        read_telegram_mock.return_value = self._generate_data()
        print(read_telegram_mock.return_value)
        return
        call_command('dsmr_datalogger')

    def _generate_data(self):
        """ Generates 'random' data, but in a way that it keeps incrementing. """
        now = datetime.now()  # Must be naive.

        # 1420070400: 01 Jan 2015 00:00:00 GMT
        second_since = int(time.time() - 1420070400)
        electricity_base = second_since * 0.00005  # Averages around 1500/1600 kWh for a year.

        electricity_1 = electricity_base
        electricity_2 = electricity_1 * 0.8  # Consumption during daylight is a bit lower.
        electricity_1_returned = electricity_1 * 0.1  # Random though of solar panel during night.
        electricity_2_returned = electricity_1 * 1.05  # Random number.

        gas = electricity_base * 0.6  # Random as well.

        currently_delivered = random.randint(0, 1500) * 0.001  # kW
        currently_returned = random.randint(0, 2500) * 0.001  # kW

        return ''.join([
            "/XMX5LGBBFFB231117727\n",
            "\n",
            "\n",
            "1-3:0.2.8(40)\n",
            "0-0:1.0.0({timestamp}W)\n".format(
                timestamp=now.strftime('%y%m%d%H%M%S')
            ),
            "0-0:96.1.1(FAKE-FAKE-FAKE-FAKE-FAKE)\n",
            "1-0:1.8.1({0:0>6}*kWh)\n".format(self._round_precision(electricity_1)),
            "1-0:2.8.1({0:0>6}*kWh)\n".format(self._round_precision(electricity_2)),
            "1-0:1.8.2({0:0>6}*kWh)\n".format(self._round_precision(electricity_1_returned)),
            "1-0:2.8.2({0:0>6}*kWh)\n".format(self._round_precision(electricity_2_returned)),
            "0-0:96.14.0(0001)\n",
            "1-0:1.7.0({0:0>2}*kW)\n".format(self._round_precision(currently_delivered)),
            "1-0:2.7.0({0:0>2}*kW)\n".format(self._round_precision(currently_returned)),
            "0-0:17.0.0(999.9*kW)\n",
            "0-0:96.3.10(1)\n",
            "0-0:96.7.21(00003)\n",
            "0-0:96.7.9(00000)\n",
            "1-0:99.97.0(0)(0-0:96.7.19)\n",
            "1-0:32.32.0(00001)\n",
            "1-0:52.32.0(00002)\n",
            "1-0:72.32.0(00003)\n",
            "1-0:32.36.0(00000)\n",
            "1-0:52.36.0(00000)\n",
            "1-0:72.36.0(00000)\n",
            "0-0:96.13.1()\n",
            "0-0:96.13.0()\n",
            "1-0:31.7.0(000*A)\n",
            "1-0:51.7.0(000*A)\n",
            "1-0:71.7.0(001*A)\n",
            "1-0:21.7.0(00.000*kW)\n",
            "1-0:41.7.0(00.000*kW)\n",
            "1-0:61.7.0({:0^2}*kW)\n".format(self._round_precision(currently_delivered)),
            "1-0:22.7.0(00.000*kW)\n",
            "1-0:42.7.0(00.000*kW)\n",
            "1-0:62.7.0(00.000*kW)\n",
            "0-1:24.1.0(003)\n",
            "0-1:96.1.0(FAKE-FAKE-FAKE-FAKE-FAKE)\n",
            "0-1:24.2.1({}W)({0:0>6}*m3)\n".format(
                now.strftime('%y%m%d%H0000'), self._round_precision(gas)
            ),
            "0-1:24.4.0(1)\n",
            "!D19A\n",
        ])

    def _round_precision(self, float_number):
        """ Round the price to two decimals. """
        if not isinstance(float_number, Decimal):
            float_number = Decimal(str(float_number))

        return float_number.quantize(Decimal('.001'), rounding=ROUND_UP)
