from django.test import TestCase
from django.utils import timezone

from dsmr_weather.models.reading import TemperatureReading


class TestTemperatureReading(TestCase):
    def setUp(self):
        self.instance = TemperatureReading.objects.create(
            read_at=timezone.now(),
            degrees_celcius=20,
        )

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'TemperatureReading')
