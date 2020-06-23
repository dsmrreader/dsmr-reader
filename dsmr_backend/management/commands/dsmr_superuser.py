from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from decouple import config


class Command(BaseCommand):  # noqa
    help = 'Persists or updates a superuser, as defined by the DSMR_USER and DSMR_PASSWORD environment vars.'

    def handle(self, **options):
        """ WARNING: Only safe for command line execution. Do NOT use for web requests! """
        username = config('DSMR_USER')
        password = config('DSMR_PASSWORD')

        if not username or not password:
            raise CommandError('DSMR_USER or DSMR_PASSWORD (or both) are empty')

        try:
            user = User.objects.get(
                username=username,
                is_superuser=True
            )
        except User.DoesNotExist:
            print('Creating new superuser "{}" (DSMR_USER)'.format(username))
            User.objects.create_superuser(username, '{}@localhost'.format(username), password)
        else:
            print('Updating password of superuser "{}" (DSMR_USER)'.format(username))
            user.set_password(password)
            user.save()
