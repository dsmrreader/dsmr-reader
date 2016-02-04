import warnings

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.core.management import call_command


class Command(BaseCommand):
    help = _('Polls the serial port for DSMR telegram and performs a reading.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--com_port',
            '-c',
            type=str,
            dest='com_port',
            default='/dev/ttyUSB0',
            help=_('COM-port connected to Smartmeter (default: %(default)s)')
        )

    def handle(self, **options):
        # Temporary for backwards compatibility
        warnings.showwarning(
            _('dsmr_stats_datalogger is DEPRECATED, and will be REMOVED in v1.0, please use dsmr_datalogger'),
            DeprecationWarning, __file__, 0
        )

        call_command("dsmr_datalogger", **options)
