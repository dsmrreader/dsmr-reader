from django.test import TestCase

from dsmr_stats.models.statistics import DayStatistics


# class TestElectricityStatistics(TestCase):
#     def test_is_equal(self):
#         """ Tests is_equal() method. """
#         stat1 = ElectricityStatistics()
#         stat2 = ElectricityStatistics()
#         self.assertTrue(stat1.is_equal(stat2))
#         self.assertTrue(stat2.is_equal(stat1))
# 
#         # ID's should be kept out of scope.
#         stat1.id = 1
#         stat2.id = 2
#         self.assertTrue(stat1.is_equal(stat2))
#         self.assertTrue(stat2.is_equal(stat1))
# 
#         stat1.power_failure_count = 0
#         stat2.power_failure_count = 1
#         self.assertFalse(stat1.is_equal(stat2))
#         self.assertFalse(stat2.is_equal(stat1))
