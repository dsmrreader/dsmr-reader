from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_datalogger.models.settings import DataloggerSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = DataloggerSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(DataloggerSettings))

    def test_baud_rate(self):
        self.assertEqual(self.instance.baud_rate, 115200)

    def test_com_port(self):
        self.assertEqual(self.instance.com_port, '/dev/ttyUSB0')
