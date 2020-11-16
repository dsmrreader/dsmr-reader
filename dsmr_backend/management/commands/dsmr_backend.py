import logging

from django.core.management.base import BaseCommand

from django.utils.translation import gettext as _

from dsmr_backend.backend_runner import run_mule


logger = logging.getLogger('dsmrreader')


class Command(BaseCommand):
    help = 'Backend operations in a persistent process'

    def add_arguments(self, parser):
        parser.add_argument(
            '--run-once',
            action='store_true',
            dest='run_once',
            default=False,
            help=_('Forces single run, overriding Infinite Command mixin')
        )

    def handle(self, *args, **kwargs):
        run_mule(**kwargs)
