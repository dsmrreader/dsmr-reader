import os
import logging

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Persists or updates a superuser, as defined by the DSMR_USER and DSMR_PASSWORD environment vars.'

    def handle(self, **options):
        """ WARNING: Only safe for command line execution. Do NOT use for web requests! """
        username = os.environ.get('DSMR_USER')
        password = os.environ.get('DSMR_PASSWORD')

        if not username:
            raise CommandError('"DSMR_USER" not specified as environment variable')

        if not password:
            raise CommandError('"DSMR_PASSWORD" not specified as environment variable')

        try:
            user = User.objects.get(
                username=username,
                is_superuser=True
            )
        except User.DoesNotExist:
            logging.info('Creating new superuser %s', username)
            User.objects.create_superuser(username, '{}@localhost'.format(username), password)
        else:
            logging.info('Updating password of superuser %s', username)
            user.set_password(password)
            user.save()
