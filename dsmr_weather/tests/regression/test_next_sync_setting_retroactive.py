from django.db.migrations.executor import MigrationExecutor
from django.test import TestCase
from django.db import connection
from django.apps import apps
from django.utils import timezone
from django.db.migrations.recorder import MigrationRecorder

from dsmr_weather.models.reading import TemperatureReading
from dsmr_weather.models.settings import WeatherSettings


class TestRegression(TestCase):
    """
    Regression for: NoReverseMatch at / Reverse for 'docs' #175.
    Thanks to: https://www.caktusgroup.com/blog/2016/02/02/writing-unit-tests-django-migrations/
    """

    @property
    def app(self):
        return apps.get_containing_app_config(type(self).__module__).name

    def test_next_sync_setting_retroactive(self):
        """ Test whether the migration can also handle existing data. """
        now = timezone.now().replace(microsecond=0)

        TemperatureReading.objects.create(
            read_at=now + timezone.timedelta(hours=1),
            degrees_celcius=20,
        )
        TemperatureReading.objects.create(
            read_at=now,
            degrees_celcius=20,
        )

        self.assertIsNone(WeatherSettings.get_solo().next_sync)

        # Now we fake applying the migration (again for this test).
        MigrationRecorder.Migration.objects.filter(
            app='dsmr_weather', name='0004_next_sync_setting_retroactive'
        ).delete()
        MigrationExecutor(connection=connection).migrate([(self.app, '0004_next_sync_setting_retroactive')])

        # When having existing data, next_sync should be based on latest reading.
        self.assertEqual(WeatherSettings.get_solo().next_sync, now + timezone.timedelta(hours=2))
