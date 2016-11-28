from django.test import TestCase
from django.contrib.admin.sites import site

from dsmr_consumption.models.settings import ConsumptionSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = ConsumptionSettings().get_solo()

    def test_admin(self):
        """ Model should be registered in Django Admin. """
        self.assertTrue(site.is_registered(ConsumptionSettings))

    def test_to_string(self):
        self.assertNotEqual(str(self.instance), '{} object'.format(self.instance.__class__.__name__))

    def test_compactor_grouping_type(self):
        self.assertEqual(
            self.instance.compactor_grouping_type, ConsumptionSettings.COMPACTOR_GROUPING_BY_MINUTE
        )
