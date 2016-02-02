from django.test import TestCase

from dsmr_consumption.models.settings import ConsumptionSettings


class TestSettings(TestCase):
    """ Tests for settings defaults. """
    def setUp(self):
        self.instance = ConsumptionSettings().get_solo()

    def test_compactor_grouping_type(self):
        self.assertEqual(
            self.instance.compactor_grouping_type, ConsumptionSettings.COMPACTOR_GROUPING_BY_MINUTE
        )
