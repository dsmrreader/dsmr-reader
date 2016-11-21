from django.test import TestCase
from django.utils import timezone

from dsmr_consumption.models.consumption import ElectricityConsumption, GasConsumption


class TestElectricityConsumption(TestCase):
    def setUp(self):
        self.instance = ElectricityConsumption.objects.create(
            read_at=timezone.now(),
            delivered_1=2,
            returned_1=2,
            delivered_2=4,
            returned_2=4,
            currently_delivered=20,
            currently_returned=40,
        )

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'ElectricityConsumption')


class TestGasConsumption(TestCase):
    def setUp(self):
        self.instance = GasConsumption.objects.create(
            read_at=timezone.now(),
            delivered=100,
            currently_delivered=1,
        )

    def test_str(self):
        """ Model should override string formatting. """
        self.assertNotEqual(str(self.instance), 'GasConsumption')
