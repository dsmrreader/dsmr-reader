from django.test import TestCase

from dsmr_datalogger.models.statistics import MeterStatistics, MeterStatisticsChange


class TestMeterStatistics(TestCase):
    def setUp(self):
        self.instance = MeterStatistics.get_solo()

    def test_ordering(self):
        """Test whether defaults allow the creation of any empty model."""
        MeterStatistics.get_solo()
        self.assertTrue(MeterStatistics.objects.exists())

    def test_str(self):
        """Model should override string formatting."""
        self.assertNotEqual(str(self.instance), "MeterStatistics")


class TestMeterStatisticsChange(TestCase):
    def setUp(self):
        self.instance = MeterStatisticsChange.objects.create(
            field="test",
            old_value="old",
            new_value="new",
        )

    def test_str(self):
        """Model should override string formatting."""
        self.assertNotEqual(str(self.instance), "MeterStatisticsChange")
