from decimal import Decimal, ROUND_UP
import logging
import random
import time
import math

import crcmod
import serial
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings

from dsmr_backend.mixins import InfiniteManagementCommandMixin
import dsmr_datalogger.services.datalogger


logger = logging.getLogger("dsmrreader")


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = "Generates a FAKE reading. DO NOT USE in production! Used for integration checks."
    name = __name__  # Required for PID file.
    sleep_time = 3

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--use-demo-mode-and-override-checks",
            action="store_true",
            dest="use_demo_mode_and_override_checks",
            default=False,
            help="Optional for production: Override checks and runs in demo mode. NEVER USE THIS",
        )
        parser.add_argument(
            "--with-gas",
            action="store_true",
            dest="with_gas",
            default=False,
            help="Optional: Include gas consumption",
        )
        parser.add_argument(
            "--with-electricity-returned",
            action="store_true",
            dest="with_electricity_returned",
            default=False,
            help="Optional: Include electricity returned (PV)",
        )
        parser.add_argument(
            "--hour-offset",
            action="store",
            dest="hour_offset",
            default=0,
            help="Optional: The offset in hours, can both be positive as negative (to go back in time).",
        )
        parser.add_argument(
            "--serial-port",
            action="store",
            dest="serial_port",
            default=None,
            metavar="/path/to/port",
            help="Optional: The serial port to write the telegram to. Useful to simulate a real port.",
        )

    def run(self, **options):
        """InfiniteManagementCommandMixin listens to handle() and calls run() in a loop."""
        if not settings.DEBUG and not options["use_demo_mode_and_override_checks"]:
            raise CommandError(
                _("Intended usage is NOT production! Only allowed when DEBUG = True")
            )

        telegram = self._generate_data(
            options["with_gas"],
            options["with_electricity_returned"],
            options["hour_offset"],
        )

        # Either write to port or just handle internally (default behaviour)
        if options["serial_port"]:
            logger.debug("Writing data to: %s", options["serial_port"])
            self._write_to_port(serial_port=options["serial_port"], data=telegram)
        else:
            logger.debug("Writing data to: internal service")
            dsmr_datalogger.services.datalogger.telegram_to_reading(data=telegram)

    def _write_to_port(self, serial_port, data):
        serial_handle = serial.Serial(
            port=serial_port,
            baudrate=115200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=1,
            rtscts=0,
            timeout=0.5,
        )
        serial_handle.write(bytes(data, "utf-8"))

    def _generate_data(self, with_gas, with_electricity_returned, hour_offset):
        """Generates 'random' data, but in a way that it keeps incrementing."""
        now = timezone.now() + timezone.timedelta(hours=int(hour_offset))
        now = timezone.localtime(now)  # Must be local.

        # COS or SIN for some fancy graphs.
        graph_base = math.cos(now.timestamp() / 20)

        current_unix_time = time.mktime(now.timetuple())
        second_since = int(
            current_unix_time - 1420070400
        )  # 1420070400: 01 Jan 2015 00:00:00 GMT
        electricity_base = second_since * 0.0001  # Averages around 3000 kWh for a year.

        electricity_1 = electricity_base
        electricity_2 = (
            electricity_1 * 0.6
        )  # Consumption during daylight is a bit lower.
        electricity_1_returned = electricity_base * 0.2  # Low return on low tariff
        electricity_2_returned = electricity_base * 0.8
        gas = electricity_base * 0.3  # Random as well.

        # Delivered and returned MAY be used simultaneously.
        # Some phases will return zero, even though the numbers make no sense.
        current_base = abs(graph_base)
        currently_delivered_l1 = 0
        currently_delivered_l2 = current_base + random.randint(0, 25) * 0.001  # kW
        currently_delivered_l3 = current_base + random.randint(0, 100) * 0.001  # kW
        currently_delivered = (
            currently_delivered_l1 + currently_delivered_l2 + currently_delivered_l3
        )
        currently_returned_l1 = current_base + random.randint(0, 40) * 0.001  # kW
        currently_returned_l2 = 0
        currently_returned_l3 = 0
        currently_returned = (
            currently_returned_l1 + currently_returned_l2 + currently_returned_l3
        )

        # Voltage around 235 with 210 and 260 as bound (+ few random Volt)
        voltage_base = 235 + ((graph_base * 100) / 5)
        phase_voltage_l1 = Decimal(random.randint(1, 2) + voltage_base)
        phase_voltage_l2 = Decimal(random.randint(3, 4) + voltage_base)
        phase_voltage_l3 = Decimal(random.randint(6, 8) + voltage_base)

        phase_power_current_l1 = random.randint(5, 8)
        phase_power_current_l2 = random.randint(2, 3)
        phase_power_current_l3 = random.randint(0, 1)

        data = [
            "/XMX5LGBBFFB123456789\r\n",
            "\r\n",
            "1-3:0.2.8(50)\r\n",
            "0-0:1.0.0({timestamp}W)\r\n".format(
                timestamp=now.strftime("%y%m%d%H%M%S")
            ),
            "0-0:96.1.1(12345678901234567890123456789000)\r\n",
            "1-0:1.8.1({}*kWh)\r\n".format(self._round_precision(electricity_1, 10)),
            "1-0:2.8.1({}*kWh)\r\n".format(
                self._round_precision(electricity_1_returned, 10)
            ),
            "1-0:1.8.2({}*kWh)\r\n".format(self._round_precision(electricity_2, 10)),
            "1-0:2.8.2({}*kWh)\r\n".format(
                self._round_precision(electricity_2_returned, 10)
            ),
            "0-0:96.14.0(0001)\r\n",  # Should switch high/low tariff, but not used anyway.
            "1-0:1.7.0({}*kW)\r\n".format(
                self._round_precision(currently_delivered, 6)
            ),
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
            "1-0:32.7.0({}*V)\r\n".format(self._round_precision(phase_voltage_l1, 1)),
            "1-0:52.7.0({}*V)\r\n".format(self._round_precision(phase_voltage_l2, 1)),
            "1-0:72.7.0({}*V)\r\n".format(self._round_precision(phase_voltage_l3, 1)),
            "1-0:31.7.0({}*A)\r\n".format(phase_power_current_l1),
            "1-0:51.7.0({}*A)\r\n".format(phase_power_current_l2),
            "1-0:71.7.0({}*A)\r\n".format(phase_power_current_l3),
            "1-0:21.7.0({}*kW)\r\n".format(
                self._round_precision(currently_delivered_l1, 6)
            ),
            "1-0:41.7.0({}*kW)\r\n".format(
                self._round_precision(currently_delivered_l2, 6)
            ),
            "1-0:61.7.0({}*kW)\r\n".format(
                self._round_precision(currently_delivered_l3, 6)
            ),
            "1-0:22.7.0({}*kW)\r\n".format(
                self._round_precision(currently_returned_l1, 6)
            ),
            "1-0:42.7.0({}*kW)\r\n".format(
                self._round_precision(currently_returned_l2, 6)
            ),
            "1-0:62.7.0({}*kW)\r\n".format(
                self._round_precision(currently_returned_l3, 6)
            ),
        ]

        if with_gas:
            # Evens out the grouping per interval a bit.
            gas_timestamp = dsmr_datalogger.services.datalogger.calculate_fake_gas_reading_timestamp(
                now, True
            )
            data += [
                "0-1:24.1.0(003)\r\n",
                "0-1:96.1.0(12345678901234567890123456789001)\r\n",
                "0-1:24.2.1({}W)({}*m3)\r\n".format(
                    gas_timestamp.strftime("%y%m%d%H%M00"),
                    self._round_precision(gas, 9),
                ),
            ]

        data += ["!"]
        telegram = "".join(data)

        # Sign the data with CRC as well.
        crc16_function = crcmod.predefined.mkPredefinedCrcFun("crc16")

        unicode_telegram = telegram.encode("ascii")
        calculated_checksum = crc16_function(unicode_telegram)

        hexed_checksum = hex(calculated_checksum)[2:].upper()
        hexed_checksum = "{:0>4}".format(
            hexed_checksum
        )  # Zero any spacing on the left hand size.

        return "{}{}\n".format(telegram, hexed_checksum)

    def _round_precision(self, float_number, fill_count):
        """Rounds the number for precision."""
        if not isinstance(float_number, Decimal):
            float_number = Decimal(str(float_number))

        rounded = float_number.quantize(Decimal(".001"), rounding=ROUND_UP)
        return str(rounded).zfill(fill_count)
