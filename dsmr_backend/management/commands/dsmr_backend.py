import logging

from django.core.management.base import BaseCommand

from dsmr_backend.mixins import InfiniteManagementCommandMixin

from dsmr_backend.backend_runner import run_mule


logger = logging.getLogger('dsmrreader')


class Command(InfiniteManagementCommandMixin, BaseCommand):
    help = 'Backend operations in a persistent process'

    def handle(self, *args, **kwargs):
        run_mule(**kwargs)
