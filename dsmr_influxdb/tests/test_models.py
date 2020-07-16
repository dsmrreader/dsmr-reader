from django.test import TestCase
from django.contrib.admin.sites import site
from django.utils import timezone

from dsmr_influxdb.models import InfluxdbIntegrationSettings, InfluxdbMeasurement


class TestInfluxdbIntegrationSettings(TestCase):
    def setUp(self):
        self.instance = InfluxdbIntegrationSettings.get_solo()

    def test_admin(self):
        self.assertTrue(site.is_registered(InfluxdbIntegrationSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))


class TestInfluxdbMeasurement(TestCase):
    def setUp(self):
        self.instance = InfluxdbMeasurement(
            time=timezone.now(),
            measurement_name='Some value',
            fields=''
        )

    def test_admin(self):
        self.assertTrue(site.is_registered(InfluxdbMeasurement))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))
