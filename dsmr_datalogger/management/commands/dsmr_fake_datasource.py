from decimal import Decimal, ROUND_UP
import random
import time

import crcmod
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import ugettext as _
from django.utils import timezone
from django.conf import settings

from dsmr_backend.mixins import InfiniteManagementCommandMixin
import dsmr_datalogger.services


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = _('Generates a FAKE reading. DO NOT USE in production! Used for integration checks.')
    name = __name__  # Required for PID file.
    sleep_time = 1

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            '--ack-to-mess-up-my-data',
            action='store_true',
            dest='acked_warning',
            default=False,
            help=_('Required option to acknowledge you that you WILL mess up your data with this.')
        )
        parser.add_argument(
            '--with-gas',
            action='store_true',
            dest='with_gas',
            default=False,
            help=_('Include gas consumption')
        )
        parser.add_argument(
            '--with-electricity-returned',
            action='store_true',
            dest='with_electricity_returned',
            default=False,
            help=_('Include electricity returned (solar panels)')
        )
        parser.add_argument(
            '--hour-offset',
            action='store',
            dest='hour_offset',
            default=0,
            help=_('The offset in hours, can both be positive as negative (to go back in time).')
        )

    def run(self, **options):
        """ InfiniteManagementCommandMixin listens to handle() and calls run() in a loop. """
        if not settings.DEBUG:
            raise CommandError(_('Intended usage is NOT production! Only allowed when DEBUG = True'))

        if not options.get('acked_warning'):
            raise CommandError(_('Intended usage is NOT production! Force by using --ack-to-mess-up-my-data'))

        telegram = self._generate_data(
            options['with_gas'],
            options['with_electricity_returned'],
            options['hour_offset']
        )
        print(telegram)  # For convenience

        dsmr_datalogger.services.telegram_to_reading(data=telegram)

    def _generate_data(self, with_gas, with_electricity_returned, hour_offset):
        """ Generates 'random' data, but in a way that it keeps incrementing. """
        now = timezone.now() + timezone.timedelta(hours=int(hour_offset))
        now = timezone.localtime(now)  # Must be local.

        self.stdout.write('-' * 32)
        self.stdout.write(str(now))
        self.stdout.write('with gas: {}'.format(with_gas))
        self.stdout.write('with electricity returned: {}'.format(with_electricity_returned))
        self.stdout.write('-' * 32)
        self.stdout.write('')

        # 1420070400: 01 Jan 2015 00:00:00 GMT
        current_unix_time = time.mktime(now.timetuple())
        second_since = int(current_unix_time - 1420070400)
        electricity_base = second_since * 0.00005  # Averages around 1500/1600 kWh for a year.

        electricity_1 = electricity_base
        electricity_2 = electricity_1 * 0.6  # Consumption during daylight is a bit lower.
        electricity_1_returned = 0
        electricity_2_returned = 0
        gas = electricity_base * 0.3  # Random as well.

        currently_delivered = random.randint(0, 1500) * 0.001  # kW
        currently_returned = 0

        if with_electricity_returned:
            electricity_1_returned = electricity_1 * 0.1  # Random though of solar panel during night.
            electricity_2_returned = electricity_1 * 1.25  # Random number.
            currently_returned = random.randint(0, 2500) * 0.001  # kW

        data = [
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(40)\r\n",
            "0-0:1.0.0({timestamp}W)\r\n".format(
                timestamp=now.strftime('%y%m%d%H%M%S')
            ),
            "0-0:96.1.1(FAKE-FAKE-FAKE-FAKE-FAKE)\r\n",
            "1-0:1.8.1({}*kWh)\r\n".format(self._round_precision(electricity_1, 10)),
            "1-0:2.8.1({}*kWh)\r\n".format(self._round_precision(electricity_1_returned, 10)),
            "1-0:1.8.2({}*kWh)\r\n".format(self._round_precision(electricity_2, 10)),
            "1-0:2.8.2({}*kWh)\r\n".format(self._round_precision(electricity_2_returned, 10)),
            "0-0:96.14.0(0001)\r\n",  # Should switch high/low tariff, but not used anyway.
            "1-0:1.7.0({}*kW)\r\n".format(self._round_precision(currently_delivered, 6)),
            "1-0:2.7.0({}*kW)\r\n".format(self._round_precision(currently_returned, 6)),
            "0-0:96.7.21(00003)\r\n",
            "0-0:96.7.9(00000)\r\n",
            "1-0:99.97.0(0)(0-0:96.7.19)\r\n",
            "1-0:32.32.0(00001)\r\n",
            "1-0:52.32.0(00002)\r\n",
            "1-0:72.32.0(00003)\r\n",
            "1-0:32.36.0(00000)\r\n",
            "1-0:52.36.0(00000)\r\n",
            "1-0:72.36.0(00000)\r\n",
            "0-0:96.13.1()\r\n",
            "0-0:96.13.0()\r\n",
            "1-0:31.7.0(000*A)\r\n",
            "1-0:51.7.0(000*A)\r\n",
            "1-0:71.7.0(001*A)\r\n",
            "1-0:21.7.0({}*kW)\r\n".format(self._round_precision(currently_delivered * 0.5, 6)),
            "1-0:41.7.0({}*kW)\r\n".format(self._round_precision(currently_delivered * 0.75, 6)),
            "1-0:61.7.0({}*kW)\r\n".format(self._round_precision(currently_delivered, 6)),
            "1-0:22.7.0({}*kW)\r\n".format(self._round_precision(currently_returned * 0.5, 6)),
            "1-0:42.7.0({}*kW)\r\n".format(self._round_precision(currently_returned * 0.75, 6)),
            "1-0:62.7.0({}*kW)\r\n".format(self._round_precision(currently_returned, 6)),
        ]

        if with_gas:
            data += [
                "0-1:24.1.0(003)\r\n",
                "0-1:96.1.0(FAKE-FAKE-FAKE-FAKE-FAKE)\r\n",
                "0-1:24.2.1({}W)({}*m3)\r\n".format(
                    now.strftime('%y%m%d%H0000'), self._round_precision(gas, 9)
                ),
            ]

        data += ["!"]
        telegram = "".join(data)

        # Sign the data with CRC as well.
        crc16_function = crcmod.predefined.mkPredefinedCrcFun('crc16')

        unicode_telegram = telegram.encode('ascii')
        calculated_checksum = crc16_function(unicode_telegram)

        hexed_checksum = hex(calculated_checksum)[2:].upper()
        hexed_checksum = '{:0>4}'.format(hexed_checksum)  # Zero any spacing on the left hand size.

        return "{}{}".format(telegram, hexed_checksum)

    def _round_precision(self, float_number, fill_count):
        """ Rounds the number for precision. """
        if not isinstance(float_number, Decimal):
            float_number = Decimal(str(float_number))

        rounded = float_number.quantize(Decimal('.001'), rounding=ROUND_UP)
        return str(rounded).zfill(fill_count)
